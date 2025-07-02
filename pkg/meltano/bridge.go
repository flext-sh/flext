package meltano

/*
#cgo pkg-config: python3
#include <Python.h>
#include <stdlib.h>

// Bridge to call Python meltano_bridge functions
static PyObject* call_python_function(const char* module_name, const char* func_name, const char* args) {
    PyObject *pModule, *pFunc, *pArgs, *pValue;
    
    // Import module
    pModule = PyImport_ImportModule(module_name);
    if (pModule == NULL) {
        PyErr_Print();
        return NULL;
    }
    
    // Get function
    pFunc = PyObject_GetAttrString(pModule, func_name);
    if (pFunc == NULL || !PyCallable_Check(pFunc)) {
        PyErr_Print();
        Py_DECREF(pModule);
        return NULL;
    }
    
    // Create arguments
    if (args != NULL && strlen(args) > 0) {
        pArgs = Py_BuildValue("(s)", args);
    } else {
        pArgs = PyTuple_New(0);
    }
    
    // Call function
    pValue = PyObject_CallObject(pFunc, pArgs);
    
    // Clean up
    Py_DECREF(pArgs);
    Py_DECREF(pFunc);
    Py_DECREF(pModule);
    
    return pValue;
}

static char* python_to_string(PyObject* obj) {
    if (obj == NULL) return NULL;
    
    PyObject* str_obj = PyObject_Str(obj);
    if (str_obj == NULL) return NULL;
    
    const char* str = PyUnicode_AsUTF8(str_obj);
    if (str == NULL) {
        Py_DECREF(str_obj);
        return NULL;
    }
    
    char* result = malloc(strlen(str) + 1);
    strcpy(result, str);
    
    Py_DECREF(str_obj);
    return result;
}
*/
import "C"

import (
    "encoding/json"
    "fmt"
    "runtime"
    "unsafe"
)

// Result represents a Meltano operation result
type Result struct {
    Success bool        `json:"success"`
    Data    interface{} `json:"data"`
    Error   string      `json:"error"`
}

// Bridge represents the Meltano bridge
type Bridge struct {
    initialized bool
}

// NewBridge creates a new Meltano bridge instance
func NewBridge() *Bridge {
    bridge := &Bridge{}
    bridge.Initialize()
    return bridge
}

// Initialize initializes the Python interpreter
func (b *Bridge) Initialize() error {
    if b.initialized {
        return nil
    }
    
    runtime.LockOSThread()
    
    if C.Py_IsInitialized() == 0 {
        C.Py_Initialize()
        if C.Py_IsInitialized() == 0 {
            return fmt.Errorf("failed to initialize Python interpreter")
        }
    }
    
    b.initialized = true
    return nil
}

// Finalize finalizes the Python interpreter
func (b *Bridge) Finalize() {
    if !b.initialized {
        return
    }
    
    C.Py_Finalize()
    b.initialized = false
    runtime.UnlockOSThread()
}

// callPythonFunction calls a Python function and returns the result as a string
func (b *Bridge) callPythonFunction(funcName, args string) (string, error) {
    if !b.initialized {
        return "", fmt.Errorf("Python interpreter not initialized")
    }
    
    moduleNameC := C.CString("meltano_bridge")
    funcNameC := C.CString(funcName)
    argsC := C.CString(args)
    
    defer func() {
        C.free(unsafe.Pointer(moduleNameC))
        C.free(unsafe.Pointer(funcNameC))
        C.free(unsafe.Pointer(argsC))
    }()
    
    result := C.call_python_function(moduleNameC, funcNameC, argsC)
    if result == nil {
        return "", fmt.Errorf("Python function call failed")
    }
    defer C.Py_DecRef(result)
    
    resultStr := C.python_to_string(result)
    if resultStr == nil {
        return "", fmt.Errorf("failed to convert Python result to string")
    }
    defer C.free(unsafe.Pointer(resultStr))
    
    return C.GoString(resultStr), nil
}

// IsAvailable checks if Meltano is available
func (b *Bridge) IsAvailable() bool {
    result, err := b.callPythonFunction("is_available", "")
    if err != nil {
        return false
    }
    
    return result == "True"
}

// InitProject initializes a new Meltano project
func (b *Bridge) InitProject(projectName, projectDir string) (*Result, error) {
    args := fmt.Sprintf(`"%s", "%s"`, projectName, projectDir)
    resultStr, err := b.callPythonFunction("init_project", args)
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// AddPlugin adds a plugin to the Meltano project
func (b *Bridge) AddPlugin(pluginType, pluginName, pluginVariant string) (*Result, error) {
    args := fmt.Sprintf(`"%s", "%s", "%s"`, pluginType, pluginName, pluginVariant)
    resultStr, err := b.callPythonFunction("add_plugin", args)
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// InstallPlugins installs all plugins in the project
func (b *Bridge) InstallPlugins() (*Result, error) {
    resultStr, err := b.callPythonFunction("install_plugins", "")
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// RunPipeline runs a Meltano pipeline
func (b *Bridge) RunPipeline(extractor, loader, transformer string) (*Result, error) {
    args := fmt.Sprintf(`"%s", "%s", "%s"`, extractor, loader, transformer)
    resultStr, err := b.callPythonFunction("run_pipeline", args)
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// GetPlugins gets a list of all plugins in the project
func (b *Bridge) GetPlugins() (*Result, error) {
    resultStr, err := b.callPythonFunction("get_plugins", "")
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// GetProjectInfo gets information about the current project
func (b *Bridge) GetProjectInfo() (*Result, error) {
    resultStr, err := b.callPythonFunction("get_project_info", "")
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// ExecuteCommand executes a raw Meltano command
func (b *Bridge) ExecuteCommand(command string, args []string) (*Result, error) {
    argsJSON, err := json.Marshal(args)
    if err != nil {
        return nil, fmt.Errorf("failed to marshal args: %v", err)
    }
    
    argStr := fmt.Sprintf(`"%s", "%s"`, command, string(argsJSON))
    resultStr, err := b.callPythonFunction("execute_command", argStr)
    if err != nil {
        return nil, err
    }
    
    var result Result
    if err := json.Unmarshal([]byte(resultStr), &result); err != nil {
        return nil, fmt.Errorf("failed to parse result: %v", err)
    }
    
    return &result, nil
}

// Global bridge instance
var globalBridge *Bridge

// GetBridge returns the global bridge instance
func GetBridge() *Bridge {
    if globalBridge == nil {
        globalBridge = NewBridge()
    }
    return globalBridge
}

// CleanupBridge cleans up the global bridge
func CleanupBridge() {
    if globalBridge != nil {
        globalBridge.Finalize()
        globalBridge = nil
    }
}