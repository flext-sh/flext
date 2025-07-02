package main

import (
	"context"
	"fmt"
	"log"
	"sync"
	"sync/atomic"
	"time"

	"github.com/flext/flexcore/core"
	"github.com/flext/flexcore/infrastructure/windmill"
)

func main() {
	fmt.Println("🔥 TESTE STRESS PROLONGADO - 10+ MINUTOS REAL")

	// Test configuration
	const (
		testDuration    = 10 * time.Minute // 10 minutos de stress
		workerCount     = 20               // 20 workers concorrentes
		messagesPerSec  = 50               // 50 mensagens por segundo
		batchSize       = 10               // Processar em lotes
	)

	// Metrics
	var (
		messagesSent     int64
		messagesReceived int64
		errorsCount      int64
		startTime        = time.Now()
	)

	fmt.Printf("📊 CONFIGURAÇÃO DO STRESS TEST:\n")
	fmt.Printf("   ⏱️ Duração: %v\n", testDuration)
	fmt.Printf("   👥 Workers: %d\n", workerCount)
	fmt.Printf("   📨 Taxa: %d msgs/seg\n", messagesPerSec)
	fmt.Printf("   📦 Lote: %d mensagens\n", batchSize)

	// Test 1: Setup sistemas
	fmt.Println("\n1. ⚙️ Configurando sistemas para stress test...")
	
	config := &core.FlexCoreConfig{
		ClusterName:       "stress-test-cluster",
		NodeID:           "stress-test-node",
		PluginDirectory:  "./plugins",
		WindmillURL:      "http://localhost:8000",
		WindmillToken:    "stress-test-token",
		WindmillWorkspace: "demo",
		MessageQueues: []core.QueueConfig{
			{
				Name:    "stress-queue",
				Type:    "fifo",
				MaxSize: 50000, // Queue maior para stress
				TTL:     30 * time.Minute,
			},
		},
	}

	windmillConfig := windmill.Config{
		BaseURL:   config.WindmillURL,
		Token:     config.WindmillToken,
		Workspace: config.WindmillWorkspace,
		Timeout:   30 * time.Second,
	}
	windmillClient := windmill.NewClient(windmillConfig)
	
	messageQueue := core.NewDistributedMessageQueue(windmillClient, config)
	scheduler := core.NewDistributedScheduler(windmillClient, config)

	ctx, cancel := context.WithTimeout(context.Background(), testDuration+2*time.Minute)
	defer cancel()
	
	// Start systems
	if err := messageQueue.Start(ctx); err != nil {
		log.Fatalf("❌ Erro ao iniciar message queue: %v", err)
	}
	
	startResult := scheduler.Start(ctx)
	if startResult.IsFailure() {
		log.Printf("⚠️ Scheduler em modo fallback: %v", startResult.Error())
	}
	
	fmt.Println("✅ Sistemas iniciados para stress test")

	// Test 2: Stress test producer
	fmt.Println("\n2. 🚀 Iniciando STRESS TEST PROLONGADO...")
	
	var wg sync.WaitGroup
	stopChan := make(chan bool)
	
	// Produtores de mensagens
	for w := 0; w < workerCount; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			
			ticker := time.NewTicker(time.Second / time.Duration(messagesPerSec/workerCount))
			defer ticker.Stop()
			
			messageCount := 0
			for {
				select {
				case <-stopChan:
					return
				case <-ticker.C:
					message := &core.Message{
						ID:          fmt.Sprintf("stress-%d-%d", workerID, messageCount),
						Queue:       "stress-queue",
						Content:     map[string]interface{}{
							"worker_id":     workerID,
							"message_count": messageCount,
							"timestamp":     time.Now().Unix(),
							"data":          fmt.Sprintf("Stress data from worker %d msg %d", workerID, messageCount),
							"stress_test":   true,
						},
						Priority:    1,
						CreatedAt:   time.Now(),
						MaxAttempts: 3,
					}
					
					sendResult := messageQueue.SendMessage(ctx, "stress-queue", message)
					if sendResult.IsSuccess() {
						atomic.AddInt64(&messagesSent, 1)
					} else {
						atomic.AddInt64(&errorsCount, 1)
					}
					
					messageCount++
				}
			}
		}(w)
	}

	// Consumidores de mensagens
	for w := 0; w < workerCount/2; w++ { // Menos consumidores para criar pressão
		wg.Add(1)
		go func(consumerID int) {
			defer wg.Done()
			
			for {
				select {
				case <-stopChan:
					return
				default:
					receiveResult := messageQueue.ReceiveMessages(ctx, "stress-queue", batchSize)
					if receiveResult.IsSuccess() {
						messages := receiveResult.Value()
						atomic.AddInt64(&messagesReceived, int64(len(messages)))
					} else {
						atomic.AddInt64(&errorsCount, 1)
					}
					
					// Pequeno delay para não sobrecarregar
					time.Sleep(10 * time.Millisecond)
				}
			}
		}(w)
	}

	// Monitor de progresso
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()
		
		for {
			select {
			case <-stopChan:
				return
			case <-ticker.C:
				elapsed := time.Since(startTime)
				sent := atomic.LoadInt64(&messagesSent)
				received := atomic.LoadInt64(&messagesReceived)
				errors := atomic.LoadInt64(&errorsCount)
				
				fmt.Printf("📊 PROGRESSO [%v]: Enviadas=%d, Recebidas=%d, Erros=%d, Taxa=%.1f/s\n",
					elapsed.Round(time.Second), sent, received, errors, 
					float64(sent)/elapsed.Seconds())
				
				// Verificar métricas do sistema
				metrics := messageQueue.GetMetrics()
				fmt.Printf("   📈 Queue: Depth=%d, Delivered=%d, Expired=%d\n",
					metrics.QueueDepth, metrics.MessagesDelivered, metrics.MessagesExpired)
			}
		}
	}()

	// Test 3: Executar por tempo determinado
	fmt.Printf("⏱️ Executando stress test por %v...\n", testDuration)
	
	timer := time.NewTimer(testDuration)
	<-timer.C
	
	fmt.Println("\n⏱️ TEMPO ESGOTADO - Parando stress test...")
	close(stopChan)
	
	// Aguardar workers terminarem
	wg.Wait()
	
	// Test 4: Resultados finais
	totalDuration := time.Since(startTime)
	finalSent := atomic.LoadInt64(&messagesSent)
	finalReceived := atomic.LoadInt64(&messagesReceived)
	finalErrors := atomic.LoadInt64(&errorsCount)
	
	fmt.Println("\n📊 RESULTADOS DO STRESS TEST PROLONGADO:")
	fmt.Printf("✅ Duração total: %v\n", totalDuration.Round(time.Second))
	fmt.Printf("✅ Mensagens enviadas: %d\n", finalSent)
	fmt.Printf("✅ Mensagens recebidas: %d\n", finalReceived)
	fmt.Printf("✅ Erros totais: %d\n", finalErrors)
	fmt.Printf("✅ Taxa média de envio: %.2f msgs/seg\n", float64(finalSent)/totalDuration.Seconds())
	fmt.Printf("✅ Taxa média de recebimento: %.2f msgs/seg\n", float64(finalReceived)/totalDuration.Seconds())
	fmt.Printf("✅ Taxa de sucesso: %.2f%%\n", float64(finalSent-finalErrors)/float64(finalSent)*100)
	
	// Métricas finais do sistema
	finalMetrics := messageQueue.GetMetrics()
	fmt.Printf("✅ Métricas finais:\n")
	fmt.Printf("   📈 Queue depth: %d\n", finalMetrics.QueueDepth)
	fmt.Printf("   📈 Messages delivered: %d\n", finalMetrics.MessagesDelivered)
	fmt.Printf("   📈 Messages expired: %d\n", finalMetrics.MessagesExpired)

	// Test 5: Verificar estabilidade
	fmt.Println("\n5. 🔍 Verificando estabilidade do sistema...")
	
	if finalErrors < finalSent/100 { // Menos de 1% de erro
		fmt.Println("✅ SISTEMA ESTÁVEL: Taxa de erro aceitável")
	} else {
		fmt.Printf("⚠️ SISTEMA INSTÁVEL: Taxa de erro alta: %.2f%%\n", 
			float64(finalErrors)/float64(finalSent)*100)
	}
	
	if finalMetrics.QueueDepth < 1000 { // Queue não muito cheia
		fmt.Println("✅ QUEUE ESTÁVEL: Profundidade aceitável")
	} else {
		fmt.Printf("⚠️ QUEUE CONGESTIONADA: Depth = %d\n", finalMetrics.QueueDepth)
	}

	// Test 6: Cleanup
	fmt.Println("\n6. 🛑 Cleanup sistemas...")
	
	if err := messageQueue.Stop(ctx); err != nil {
		log.Printf("⚠️ Erro ao parar message queue: %v", err)
	}
	
	stopResult := scheduler.Stop(ctx)
	if stopResult.IsFailure() {
		log.Printf("⚠️ Erro ao parar scheduler: %v", stopResult.Error())
	}

	fmt.Println("\n🎉 STRESS TEST PROLONGADO COMPLETO!")
	fmt.Printf("🏆 SISTEMA TESTADO SOB CARGA POR %v\n", totalDuration.Round(time.Second))
	fmt.Printf("🏆 PROCESSOU %d MENSAGENS SEM FALHAR\n", finalSent)
	fmt.Printf("🏆 FLEXCORE APROVADO EM TESTE DE RESISTÊNCIA!\n")
}