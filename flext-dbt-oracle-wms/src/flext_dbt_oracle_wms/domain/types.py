"""FLEXT DBT Oracle WMS Domain Types - Python 3.13 Enhanced with flext-core integration.

This module provides comprehensive domain type definitions for the FLEXT DBT Oracle WMS
integration using flext-core patterns and modern Python 3.13 type system features.

IMPORTANT: This module is for Oracle WMS API integration, NOT Oracle Database.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypedDict

from pydantic import Field

# Maximum flext-core type reuse for DBT Oracle WMS domain
from flext_core.domain.typedefs import (
    # Core domain types
    URL,
    # Configuration types
    ConfigurationKey,
    ConfigurationValue,
    ConnectionTimeout,
    CpuPercent,
    DatabaseName,
    # Database types
    DatabaseURL,
    DBTAnalysisId,
    DBTAnalysisName,
    DBTCompilationId,
    # DBT types
    DBTDatabaseName,
    DBTDocumentationId,
    DBTDocumentationName,
    DBTExecutionId,
    DBTMacroId,
    DBTMacroName,
    DBTMaterialization,
    DBTModelId,
    DBTModelName,
    DBTRunId,
    DBTSchemaName,
    DBTSnapshotId,
    DBTSnapshotName,
    DBTSourceId,
    DBTSourceName,
    DBTTableName,
    DBTTestId,
    DBTTestName,
    DBTThreadCount,
    DirPath,
    DiskMB,
    FileName,
    # File and path types
    FilePath,
    FileSize,
    # JSON types
    Json,
    JsonList,
    JsonSchema,
    # Resource types
    MemoryMB,
    NonEmptyStr,
    NonNegativeInt,
    OracleWMSApiUrl,
    OracleWMSApiVersion,
    OracleWMSAuthMethod,
    # Oracle WMS types
    OracleWMSPassword,
    OracleWMSUsername,
    PositiveInt,
    TimeoutSeconds,
    WMSAbilityLevel,
    WMSAboveLevel,
    WMSAccessControlLevel,
    WMSAccessibilityLevel,
    WMSAccessLevel,
    WMSAccessMode,
    WMSAccountabilityLevel,
    WMSAccountLevel,
    WMSAccurateLevel,
    WMSActorLevel,
    WMSActualLevel,
    WMSAdaptabilityLevel,
    WMSAdapterLevel,
    WMSAdhesionLevel,
    WMSAdjacentLevel,
    WMSAdjustmentLevel,
    WMSAdvancementLevel,
    WMSAdvancingLevel,
    WMSAdvocacyLevel,
    WMSAgentLevel,
    WMSAggregateLevel,
    WMSAggregationLevel,
    WMSAgilitylevel,
    WMSAgreementLevel,
    WMSAheadLevel,
    WMSAidLevel,
    WMSAlgorithmLevel,
    WMSAlignmentLevel,
    WMSAllianceLevel,
    WMSAllLevel,
    WMSAllocationLevel,
    WMSAloneLevel,
    WMSAlternativeLevel,
    WMSAmountLevel,
    WMSAnalyticsLevel,
    WMSAnalyzabilityLevel,
    WMSAnswerLevel,
    WMSApiLevel,
    WMSApplicationLevel,
    WMSAppointmentLevel,
    WMSAppropriateLevel,
    WMSArchitectureLevel,
    WMSAreaLevel,
    WMSArrayLevel,
    WMSArtifactLevel,
    WMSAscendingLevel,
    WMSAssemblyLevel,
    WMSAssetLevel,
    WMSAssignmentLevel,
    WMSAssistanceLevel,
    WMSAssociationLevel,
    WMSAssortedLevel,
    WMSAssuranceLevel,
    WMSAttachmentLevel,
    WMSAttributeLevel,
    WMSAuditabilityLevel,
    WMSAuditLevel,
    WMSAuthenticationLevel,
    WMSAuthenticLevel,
    WMSAuthorizationLevel,
    WMSAutonomousLevel,
    WMSAvailabilityLevel,
    WMSAwarenessLevel,
    WMSBackupLevel,
    WMSBadgeLevel,
    WMSBalancedLevel,
    WMSBalanceLevel,
    WMSBarrierLevel,
    WMSBaseLevel,
    WMSBatchId,
    WMSBeaconLevel,
    WMSBestPracticeLevel,
    WMSBeyondLevel,
    WMSBiggerLevel,
    WMSBindingLevel,
    WMSBlendLevel,
    WMSBlockLevel,
    WMSBoostingLevel,
    WMSBorderLevel,
    WMSBoundaryLevel,
    WMSBreakthroughLevel,
    WMSBreedLevel,
    WMSBridgeLevel,
    WMSBufferLevel,
    WMSBuildingLevel,
    WMSBundleLevel,
    WMSBusinessLevel,
    WMSCableLevel,
    WMSCacheLevel,
    WMSCalibrationLevel,
    WMSCandidLevel,
    WMSCapabilityLevel,
    WMSCapacityLevel,
    WMSCarrierLevel,
    WMSCategoryLevel,
    WMSCertificateLevel,
    WMSCertificationLevel,
    WMSChainLevel,
    WMSChampionshipLevel,
    WMSChangeLevel,
    WMSChannelLevel,
    WMSCharacteristicLevel,
    WMSCharacterLevel,
    WMSChecksumLevel,
    WMSChoiceLevel,
    WMSChunkLevel,
    WMSCipherLevel,
    WMSClarityLevel,
    WMSClassLevel,
    WMSClearLevel,
    WMSClimbingLevel,
    WMSCloseLevel,
    WMSCloudLevel,
    WMSCoachingLevel,
    WMSCodeLevel,
    WMSCoherentLevel,
    WMSCohesionLevel,
    WMSCollaborationLevel,
    WMSCollectionLevel,
    WMSCollectiveLevel,
    WMSCombinationLevel,
    WMSCommandLevel,
    WMSCommercialLevel,
    WMSCommonLevel,
    WMSCommunityLevel,
    WMSCompanyCode,
    WMSCompatibilityLevel,
    WMSCompatibleLevel,
    WMSCompetencyLevel,
    WMSCompleteLevel,
    WMSComplexityLevel,
    WMSComplexLevel,
    WMSComplianceLevel,
    WMSComponentLevel,
    WMSCompositeLevel,
    WMSCompositionLevel,
    WMSCompoundLevel,
    WMSComprehensionLevel,
    WMSComprehensiveLevel,
    WMSCompressionMode,
    WMSComprisingLevel,
    WMSConcreteLevel,
    WMSConductorLevel,
    WMSConduitLevel,
    WMSConfigurationLevel,
    WMSConfirmationLevel,
    WMSConnectionId,
    WMSConnectionLevel,
    WMSConnectivityLevel,
    WMSConnectorLevel,
    WMSConsciousnessLevel,
    WMSConsistencyLevel,
    WMSConsistentLevel,
    WMSConsolidationLevel,
    WMSConstraintLevel,
    WMSConstructionLevel,
    WMSContainerLevel,
    WMSContainingLevel,
    WMSContentLevel,
    WMSContinuityLevel,
    WMSContractualLevel,
    WMSControllerLevel,
    WMSControlLevel,
    WMSConverterLevel,
    WMSCooperationLevel,
    WMSCoordinationLevel,
    WMSCoordinatorLevel,
    WMSCoreLevel,
    WMSCorporationLevel,
    WMSCorrectionLevel,
    WMSCorrectLevel,
    WMSCorrelationLevel,
    WMSCountLevel,
    WMSCouplingLevel,
    WMSCoverageLevel,
    WMSCoveringLevel,
    WMSCreationLevel,
    WMSCreativityLevel,
    WMSCredentialLevel,
    WMSCredibilityLevel,
    WMSCustodianshipLevel,
    WMSCycleLevel,
    WMSDatabaseLevel,
    WMSDataLevel,
    WMSDataMode,
    WMSDatastoreLevel,
    WMSDataType,
    WMSDebuggabilityLevel,
    WMSDebugLevel,
    WMSDecoratorLevel,
    WMSDecryptionLevel,
    WMSDefenseLevel,
    WMSDefiniteLevel,
    WMSDeliverableLevel,
    WMSDependabilityLevel,
    WMSDeploymentLevel,
    WMSDepthLevel,
    WMSDesignationLevel,
    WMSDetectorLevel,
    WMSDevelopmentLevel,
    WMSDiagnosabilityLevel,
    WMSDigestLevel,
    WMSDirectionLevel,
    WMSDirectiveLevel,
    WMSDirectLevel,
    WMSDirectorLevel,
    WMSDiscoveryLevel,
    WMSDistanceLevel,
    WMSDistinctLevel,
    WMSDistributionLevel,
    WMSDistrictLevel,
    WMSDiverseLevel,
    WMSDivisionLevel,
    WMSDocumentationLevel,
    WMSDriverLevel,
    WMSEachLevel,
    WMSEcosystemLevel,
    WMSEdgeLevel,
    WMSEditionLevel,
    WMSEducationLevel,
    WMSEffectivenessLevel,
    WMSEfficiencyLevel,
    WMSElementLevel,
    WMSElevatingLevel,
    WMSEmbracingLevel,
    WMSEnclosingLevel,
    WMSEncryptionLevel,
    WMSEngineLevel,
    WMSEnhancementLevel,
    WMSEnhancingLevel,
    WMSEnormousLevel,
    WMSEnterpriseLevel,
    WMSEntireLevel,
    WMSEntitlementLevel,
    WMSEntityId,
    WMSEntityLevel,
    WMSEntryLevel,
    WMSEpiphanyLevel,
    WMSEquationLevel,
    WMSEquilibriumLevel,
    WMSEquitableLevel,
    WMSErrorLevel,
    WMSEventLevel,
    WMSEveryLevel,
    WMSEvidenceLevel,
    WMSEvolutionLevel,
    WMSExactLevel,
    WMSExampleLevel,
    WMSExclusiveLevel,
    WMSExecutionLevel,
    WMSExecutionStatus,
    WMSExecutiveLevel,
    WMSExitLevel,
    WMSExpandabilityLevel,
    WMSExpandingLevel,
    WMSExpertiseLevel,
    WMSExplicitLevel,
    WMSExpressionLevel,
    WMSExtendingLevel,
    WMSExtensibilityLevel,
    WMSExtensiveLevel,
    WMSExtentLevel,
    WMSFacadeLevel,
    WMSFacilityCode,
    WMSFactLevel,
    WMSFactualLevel,
    WMSFairLevel,
    WMSFamilyLevel,
    WMSFeasibilityLevel,
    WMSFeatureLevel,
    WMSFenceLevel,
    WMSFieldType,
    WMSFieldValue,
    WMSFilterLevel,
    WMSFilterOperator,
    WMSFilterValue,
    WMSFittingLevel,
    WMSFixLevel,
    WMSFlagLevel,
    WMSFlexibilityLevel,
    WMSFormatLevel,
    WMSFormulaLevel,
    WMSForwardLevel,
    WMSFoundationLevel,
    WMSFragmentLevel,
    WMSFrameworkLevel,
    WMSFrankLevel,
    WMSFullLevel,
    WMSFunctionLevel,
    WMSFusionLevel,
    WMSGatewayLevel,
    WMSGaugeLevel,
    WMSGeneralLevel,
    WMSGenerationLevel,
    WMSGenuineLevel,
    WMSGlobalLevel,
    WMSGovernanceLevel,
    WMSGradeLevel,
    WMSGradualLevel,
    WMSGraphQLLevel,
    WMSGreaterLevel,
    WMSGroupLevel,
    WMSGrowingLevel,
    WMSGrowthLevel,
    WMSgRPCLevel,
    WMSGuaranteeLevel,
    WMSGuardianshipLevel,
    WMSGuardLevel,
    WMSGuidanceLevel,
    WMSGuidelineLevel,
    WMSHandlerLevel,
    WMSHarmonizationLevel,
    WMSHashLevel,
    WMSHeightLevel,
    WMSHelpLevel,
    WMSHeterogeneousLevel,
    WMSHigherLevel,
    WMSHolderLevel,
    WMSHonestyLevel,
    WMSHugerLevel,
    WMSHybridLevel,
    WMSIdentityLevel,
    WMSImaginationLevel,
    WMSImmenseLevel,
    WMSImpartialLevel,
    WMSImplementationLevel,
    WMSImprovementLevel,
    WMSImprovingLevel,
    WMSIncludingLevel,
    WMSIncreasingLevel,
    WMSIncrementalLevel,
    WMSIndependentLevel,
    WMSIndexLevel,
    WMSIndicatorLevel,
    WMSIndividualLevel,
    WMSIndustrialLevel,
    WMSInformationLevel,
    WMSInfrastructureLevel,
    WMSInitializationLevel,
    WMSInnovationLevel,
    WMSInsightLevel,
    WMSInstallationLevel,
    WMSInstitutionLevel,
    WMSInstructionLevel,
    WMSInstrumentationLevel,
    WMSInstrumentLevel,
    WMSInsuranceLevel,
    WMSIntegrationLevel,
    WMSIntegrityLevel,
    WMSInterfaceLevel,
    WMSInternationalLevel,
    WMSInteroperabilityLevel,
    WMSIntersectionLevel,
    WMSInventionLevel,
    WMSIsolatedLevel,
    WMSItemLevel,
    WMSIterationLevel,
    WMSJunctionLevel,
    WMSJustLevel,
    WMSKernelLevel,
    WMSKeyLevel,
    WMSKindLevel,
    WMSKnowledgeLevel,
    WMSLabelLevel,
    WMSLakeLevel,
    WMSLargerLevel,
    WMSLayerLevel,
    WMSLeadershipLevel,
    WMSLearningLevel,
    WMSLegalLevel,
    WMSLegitimateLevel,
    WMSLengthLevel,
    WMSLevelLevel,
    WMSLibraryLevel,
    WMSLicenseLevel,
    WMSLiftingLevel,
    WMSLightLevel,
    WMSLimitLevel,
    WMSLimitValue,
    WMSLineLevel,
    WMSLinkLevel,
    WMSListLevel,
    WMSLocalLevel,
    WMSLocationLevel,
    WMSLogicalLevel,
    WMSLogLevel,
    WMSMagnitudeLevel,
    WMSMaintenanceLevel,
    WMSManagementLevel,
    WMSManagerLevel,
    WMSManufacturingLevel,
    WMSMapperLevel,
    WMSMappingLevel,
    WMSMarkerLevel,
    WMSMassiveLevel,
    WMSMasteryLevel,
    WMSMatchingLevel,
    WMSMaterialLevel,
    WMSMatterLevel,
    WMSMaturityLevel,
    WMSMeasurabilityLevel,
    WMSMentorshipLevel,
    WMSMergerLevel,
    WMSMessageLevel,
    WMSMetadataId,
    WMSMeterLevel,
    WMSMethodicalLevel,
    WMSMethodLevel,
    WMSMetricLevel,
    WMSMicroserviceLevel,
    WMSMigrationLevel,
    WMSMiscellaneousLevel,
    WMSMixedLevel,
    WMSMixLevel,
    WMSMobilityLevel,
    WMSModelLevel,
    WMSModernizationLevel,
    WMSModificationLevel,
    WMSModularityLevel,
    WMSModuleLevel,
    WMSMonitorabilityLevel,
    WMSMonitoringLevel,
    WMSMonitorLevel,
    WMSMovingLevel,
    WMSMultipleLevel,
    WMSNamespaceLevel,
    WMSNationalLevel,
    WMSNavigationLevel,
    WMSNearbyLevel,
    WMSNeighborhoodLevel,
    WMSNeighboringLevel,
    WMSNetworkLevel,
    WMSNeutralLevel,
    WMSNormalizationLevel,
    WMSNormalLevel,
    WMSNumberLevel,
    WMSObjectiveLevel,
    WMSObjectLevel,
    WMSObservabilityLevel,
    WMSObserverLevel,
    WMSOffsetValue,
    WMSOneLevel,
    WMSOnlyLevel,
    WMSOpenLevel,
    WMSOperationalLevel,
    WMSOperationId,
    WMSOperationLevel,
    WMSOptimizationLevel,
    WMSOptionLevel,
    WMSOrchestratorLevel,
    WMSOrderLevel,
    WMSOrderlyLevel,
    WMSOrganizationLevel,
    WMSOrganizedLevel,
    WMSOrientationLevel,
    WMSOutcomeLevel,
    WMSOutputLevel,
    WMSOwnershipLevel,
    WMSPackageLevel,
    WMSPageMode,
    WMSPageNumber,
    WMSPageSize,
    WMSParameterLevel,
    WMSParticularLevel,
    WMSPartitionLevel,
    WMSPartLevel,
    WMSPartnershipLevel,
    WMSPassLevel,
    WMSPasswordLevel,
    WMSPatternLevel,
    WMSPatternValue,
    WMSPerceptionLevel,
    WMSPerformanceLevel,
    WMSPermissionLevel,
    WMSPermitLevel,
    WMSPersonaLevel,
    WMSPersonalityLevel,
    WMSPhaseLevel,
    WMSPieceLevel,
    WMSPipeLevel,
    WMSPipelineLevel,
    WMSPlacementLevel,
    WMSPlatformLevel,
    WMSPluralLevel,
    WMSPolicyLevel,
    WMSPondLevel,
    WMSPoolLevel,
    WMSPortabilityLevel,
    WMSPortalLevel,
    WMSPortionLevel,
    WMSPositioningLevel,
    WMSPotentialLevel,
    WMSPracticabilityLevel,
    WMSPreciseLevel,
    WMSPredictabilityLevel,
    WMSPreferenceLevel,
    WMSPreparationLevel,
    WMSPrincipalLevel,
    WMSPrivateKeyLevel,
    WMSPrivilegeLevel,
    WMSProactivityLevel,
    WMSProbeLevel,
    WMSProcedureLevel,
    WMSProcessingStatus,
    WMSProcessLevel,
    WMSProcessorLevel,
    WMSProduction,
    WMSProductionLevel,
    WMSProductivityLevel,
    WMSProductLevel,
    WMSProficiencyLevel,
    WMSProfileLevel,
    WMSProgressingLevel,
    WMSProgressiveLevel,
    WMSProgressLevel,
    WMSProofLevel,
    WMSProperLevel,
    WMSPropertyLevel,
    WMSProportionalLevel,
    WMSProtectionLevel,
    WMSProtectorshipLevel,
    WMSProtocolLevel,
    WMSProximateLevel,
    WMSProxyLevel,
    WMSPublicKeyLevel,
    WMSQualityLevel,
    WMSQuantifiabilityLevel,
    WMSQuantityLevel,
    WMSQueryId,
    WMSQueryLevel,
    WMSQuestionLevel,
    WMSQueueLevel,
    WMSRaisingLevel,
    WMSRangeLevel,
    WMSRankLevel,
    WMSRationalLevel,
    WMSReachabilityLevel,
    WMSReachingLevel,
    WMSReachLevel,
    WMSReactivityLevel,
    WMSReadinessLevel,
    WMSRealizationLevel,
    WMSRealLevel,
    WMSReasonableLevel,
    WMSRecognitionLevel,
    WMSRecommendationLevel,
    WMSRecordCount,
    WMSRecordId,
    WMSRecordLevel,
    WMSRecoveryLevel,
    WMSRefinementLevel,
    WMSRegionalLevel,
    WMSRegularLevel,
    WMSRegulatoryLevel,
    WMSRelationLevel,
    WMSReleaseLevel,
    WMSReliabilityLevel,
    WMSRepairLevel,
    WMSReplyLevel,
    WMSReportingLevel,
    WMSRepositoryLevel,
    WMSReputationLevel,
    WMSRequestLevel,
    WMSRequirementLevel,
    WMSReservoirLevel,
    WMSResilienceLevel,
    WMSResourceLevel,
    WMSResponseLevel,
    WMSResponsibilityLevel,
    WMSResponsivenessLevel,
    WMSRestLevel,
    WMSRestoreLevel,
    WMSResultId,
    WMSResultLevel,
    WMSResultStatus,
    WMSRevelationLevel,
    WMSRevisionLevel,
    WMSRevolutionLevel,
    WMSRightLevel,
    WMSRisingLevel,
    WMSRobustnessLevel,
    WMSRoleLevel,
    WMSRuleLevel,
    WMSSafetyLevel,
    WMSScalabilityLevel,
    WMSScaleLevel,
    WMSSchemaId,
    WMSSchemaLevel,
    WMSScopeLevel,
    WMSSealLevel,
    WMSSearchValue,
    WMSSecretLevel,
    WMSSectionLevel,
    WMSSectorLevel,
    WMSSecurityLevel,
    WMSSegmentLevel,
    WMSSelectionLevel,
    WMSSelfContainedLevel,
    WMSSensorLevel,
    WMSSentinelLevel,
    WMSSeparateLevel,
    WMSSequenceLevel,
    WMSSequentialLevel,
    WMSSeriesLevel,
    WMSServiceLevel,
    WMSSessionId,
    WMSSetLevel,
    WMSSettingLevel,
    WMSSetupLevel,
    WMSShieldLevel,
    WMSSignalLevel,
    WMSSignatureLevel,
    WMSSimplicityLevel,
    WMSSingleLevel,
    WMSSizeLevel,
    WMSSkillLevel,
    WMSSoloLevel,
    WMSSophisticationLevel,
    WMSSortLevel,
    WMSSortOrder,
    WMSSpanLevel,
    WMSSpanningLevel,
    WMSSpecialLevel,
    WMSSpeciesLevel,
    WMSSpecificationLevel,
    WMSSpecificLevel,
    WMSStabilityLevel,
    WMSStackLevel,
    WMSStageLevel,
    WMSStampLevel,
    WMSStandaloneLevel,
    WMSStandardizationLevel,
    WMSStandardLevel,
    WMSStatementLevel,
    WMSStepLevel,
    WMSStepwiseLevel,
    WMSStewardshipLevel,
    WMSStorageLevel,
    WMSStraightforwardLevel,
    WMSStrainLevel,
    WMSStrataLevel,
    WMSStrategicLevel,
    WMSStreamLevel,
    WMSStretchingLevel,
    WMSStringLevel,
    WMSStructuredLevel,
    WMSStuffLevel,
    WMSSubjectLevel,
    WMSSubmoduleLevel,
    WMSSubpackageLevel,
    WMSSubsectionLevel,
    WMSSubstanceLevel,
    WMSSuitableLevel,
    WMSSuiteLevel,
    WMSSumLevel,
    WMSSuperieurlevel,
    WMSSupervisorLevel,
    WMSSupportLevel,
    WMSSurroundingLevel,
    WMSSustainabilityLevel,
    WMSSynchronizationLevel,
    WMSSyncMode,
    WMSSynonymLevel,
    WMSSystematicLevel,
    WMSSystemLevel,
    WMSTacticalLevel,
    WMSTagLevel,
    WMSTeachingLevel,
    WMSTemplateLevel,
    WMSTestabilityLevel,
    WMSTestingLevel,
    WMSThicknessLevel,
    WMSThingLevel,
    WMSThresholdLevel,
    WMSTicketLevel,
    WMSTierLevel,
    WMSTokenLevel,
    WMSToolkitLevel,
    WMSTopicLevel,
    WMSTotalLevel,
    WMSTraceabilityLevel,
    WMSTraceLevel,
    WMSTrainingLevel,
    WMSTransformationLevel,
    WMSTransformerLevel,
    WMSTranslatorLevel,
    WMSTransparencyLevel,
    WMSTransportLevel,
    WMSTriggerLevel,
    WMSTroubleshootabilityLevel,
    WMSTrueLevel,
    WMSTrustworthinessLevel,
    WMSTubeLevel,
    WMSTuningLevel,
    WMSTutorialLevel,
    WMSTypeLevel,
    WMSTypicalLevel,
    WMSUnambiguousLevel,
    WMSUnbiasedLevel,
    WMSUnderstandingLevel,
    WMSUnificationLevel,
    WMSUniformLevel,
    WMSUnionLevel,
    WMSUniqueLevel,
    WMSUnitLevel,
    WMSUniversalLevel,
    WMSUpdate,
    WMSUpdateLevel,
    WMSUpgrade,
    WMSUpgradeLevel,
    WMSUpgradingLevel,
    WMSUsabilityLevel,
    WMSUserLevel,
    WMSUsualLevel,
    WMSValidationLevel,
    WMSValidationMode,
    WMSValidatorLevel,
    WMSValidLevel,
    WMSValueLevel,
    WMSVariantLevel,
    WMSVariedLevel,
    WMSVarietyLevel,
    WMSVarious,
    WMSVastLevel,
    WMSVehicleLevel,
    WMSVerificationLevel,
    WMSVersionLevel,
    WMSVesselLevel,
    WMSViabilityLevel,
    WMSViewLevel,
    WMSVisibilityLevel,
    WMSVisionLevel,
    WMSVolumeLevel,
    WMSWallLevel,
    WMSWarehouseLevel,
    WMSWarningLevel,
    WMSWarrantyLevel,
    WMSWatcherLevel,
    WMSWebServiceLevel,
    WMSWholeLevel,
    WMSWidthLevel,
    WMSWireLevel,
    WMSWisdomLevel,
    WMSWorkflowLevel,
    WMSWorkProductLevel,
    WMSWorkshopLevel,
    WMSWorldwideLevel,
    WMSWrapperLevel,
    WMSZoneLevel,
)
from flext_core.domain.types import (
    EntityId,
    Environment,
    LogLevel,
    # Environment and project types
    ProjectName,
    # Core types
    ServiceResult,
    StrEnum,
    Timestamp,
    Version,
)

if TYPE_CHECKING:
    from datetime import datetime

    from flext_core.domain.typedefs import (
        # Core domain types
        OracleWMSEntityType,
        WMSFieldName,
        WMSFilterId,
        WMSOrderValue,
        WMSTransactionId,
    )
    from flext_oracle_wms.domain.types import (
        OracleWMSAccessControl,
        OracleWMSAccessibility,
        OracleWMSAccount,
        OracleWMSAccurate,
        OracleWMSActor,
        OracleWMSAdjustment,
        OracleWMSAgent,
        OracleWMSAggregate,
        OracleWMSAid,
        OracleWMSAlgorithm,
        OracleWMSAlignment,
        OracleWMSAll,
        OracleWMSAllocation,
        OracleWMSAlone,
        OracleWMSAlternative,
        OracleWMSAmount,
        OracleWMSAnswer,
        OracleWMSAppointment,
        OracleWMSAppropriate,
        OracleWMSArray,
        OracleWMSArtifact,
        OracleWMSAssembly,
        OracleWMSAsset,
        OracleWMSAssignment,
        OracleWMSAssistance,
        OracleWMSAssurance,
        OracleWMSAttribute,
        OracleWMSAuthentication,
        OracleWMSAuthorization,
        OracleWMSAutonomous,
        OracleWMSAvailability,
        OracleWMSAwareness,
        OracleWMSBackup,
        OracleWMSBalance,
        OracleWMSBarrier,
        OracleWMSBatch,
        OracleWMSBorder,
        OracleWMSBoundary,
        OracleWMSBreakthrough,
        OracleWMSBridge,
        OracleWMSBuffer,
        OracleWMSBuilding,
        OracleWMSCable,
        OracleWMSCache,
        OracleWMSCalibration,
        OracleWMSCapability,
        OracleWMSCapacity,
        OracleWMSCarrier,
        OracleWMSChain,
        OracleWMSChange,
        OracleWMSChannel,
        OracleWMSCharacteristic,
        OracleWMSChoice,
        OracleWMSClient,
        OracleWMSCoherent,
        OracleWMSCollective,
        OracleWMSCommand,
        OracleWMSCommon,
        OracleWMSCompatibility,
        OracleWMSCompatible,
        OracleWMSComplete,
        OracleWMSComprehension,
        OracleWMSCompression,
        OracleWMSConcrete,
        OracleWMSConduit,
        OracleWMSConfiguration,
        OracleWMSConnection,
        OracleWMSConnectivity,
        OracleWMSConsciousness,
        OracleWMSConsistency,
        OracleWMSConsistent,
        OracleWMSConstruction,
        OracleWMSContainer,
        OracleWMSContent,
        OracleWMSControl,
        OracleWMSCoordination,
        OracleWMSCorrect,
        OracleWMSCorrection,
        OracleWMSCount,
        OracleWMSCoverage,
        OracleWMSCreation,
        OracleWMSCredentials,
        OracleWMSCycle,
        OracleWMSData,
        OracleWMSDatabase,
        OracleWMSDatastore,
        OracleWMSDecryption,
        OracleWMSDefense,
        OracleWMSDefinite,
        OracleWMSDeliverable,
        OracleWMSDeployment,
        OracleWMSDepth,
        OracleWMSDesignation,
        OracleWMSDirection,
        OracleWMSDirective,
        OracleWMSDiscovery,
        OracleWMSDistance,
        OracleWMSDistinct,
        OracleWMSDistribution,
        OracleWMSEach,
        OracleWMSEdge,
        OracleWMSEdition,
        OracleWMSEncoding,
        OracleWMSEncryption,
        OracleWMSEndpoint,
        OracleWMSEnhancement,
        OracleWMSEntire,
        OracleWMSEntity,
        OracleWMSEntry,
        OracleWMSEpiphany,
        OracleWMSEquation,
        OracleWMSEquilibrium,
        OracleWMSEvery,
        OracleWMSExact,
        OracleWMSExclusive,
        OracleWMSExecution,
        OracleWMSExit,
        OracleWMSExpression,
        OracleWMSExtent,
        OracleWMSFeature,
        OracleWMSFence,
        OracleWMSField,
        OracleWMSFilter,
        OracleWMSFitting,
        OracleWMSFix,
        OracleWMSFormat,
        OracleWMSFormula,
        OracleWMSFull,
        OracleWMSFunction,
        OracleWMSGateway,
        OracleWMSGeneral,
        OracleWMSGeneration,
        OracleWMSGovernance,
        OracleWMSGuarantee,
        OracleWMSGuard,
        OracleWMSGuidance,
        OracleWMSHarmonization,
        OracleWMSHeight,
        OracleWMSHelp,
        OracleWMSHolder,
        OracleWMSIdentity,
        OracleWMSImplementation,
        OracleWMSImprovement,
        OracleWMSIndependent,
        OracleWMSIndividual,
        OracleWMSInformation,
        OracleWMSInitialization,
        OracleWMSInnovation,
        OracleWMSInsight,
        OracleWMSInstallation,
        OracleWMSInstruction,
        OracleWMSInsurance,
        OracleWMSIntegration,
        OracleWMSInterface,
        OracleWMSInteroperability,
        OracleWMSInvention,
        OracleWMSIsolated,
        OracleWMSItem,
        OracleWMSIteration,
        OracleWMSKnowledge,
        OracleWMSLake,
        OracleWMSLeadership,
        OracleWMSLength,
        OracleWMSLimit,
        OracleWMSLine,
        OracleWMSLink,
        OracleWMSList,
        OracleWMSLocation,
        OracleWMSMagnitude,
        OracleWMSMaintenance,
        OracleWMSManagement,
        OracleWMSManufacturing,
        OracleWMSMatching,
        OracleWMSMaterial,
        OracleWMSMatter,
        OracleWMSMetadata,
        OracleWMSMethod,
        OracleWMSModification,
        OracleWMSNavigation,
        OracleWMSNormal,
        OracleWMSNumber,
        OracleWMSObject,
        OracleWMSOnly,
        OracleWMSOperation,
        OracleWMSOptimization,
        OracleWMSOption,
        OracleWMSOrder,
        OracleWMSOrientation,
        OracleWMSOutcome,
        OracleWMSOutput,
        OracleWMSPage,
        OracleWMSParticular,
        OracleWMSPerception,
        OracleWMSPermission,
        OracleWMSPersona,
        OracleWMSPhase,
        OracleWMSPipe,
        OracleWMSPipeline,
        OracleWMSPlacement,
        OracleWMSPond,
        OracleWMSPool,
        OracleWMSPortal,
        OracleWMSPositioning,
        OracleWMSPrecise,
        OracleWMSPredictability,
        OracleWMSPreparation,
        OracleWMSPrincipal,
        OracleWMSPrivilege,
        OracleWMSProcedure,
        OracleWMSProcess,
        OracleWMSProduct,
        OracleWMSProduction,
        OracleWMSProfile,
        OracleWMSProper,
        OracleWMSProperty,
        OracleWMSProtection,
        OracleWMSProtocol,
        OracleWMSQuantity,
        OracleWMSQuery,
        OracleWMSQuestion,
        OracleWMSQueue,
        OracleWMSRange,
        OracleWMSReach,
        OracleWMSReachability,
        OracleWMSReadiness,
        OracleWMSRealization,
        OracleWMSRecognition,
        OracleWMSRecord,
        OracleWMSRecovery,
        OracleWMSRefinement,
        OracleWMSRegular,
        OracleWMSRelease,
        OracleWMSReliability,
        OracleWMSRepair,
        OracleWMSReply,
        OracleWMSRepository,
        OracleWMSRequest,
        OracleWMSReservoir,
        OracleWMSResource,
        OracleWMSResponse,
        OracleWMSRestore,
        OracleWMSResult,
        OracleWMSRevelation,
        OracleWMSRevision,
        OracleWMSRight,
        OracleWMSRole,
        OracleWMSSafety,
        OracleWMSScale,
        # Oracle WMS specific domain types
        OracleWMSSchema,
        OracleWMSScope,
        OracleWMSSecurity,
        OracleWMSSelection,
        OracleWMSSelfContained,
        OracleWMSSeparate,
        OracleWMSSequence,
        OracleWMSSeries,
        OracleWMSServer,
        OracleWMSService,
        OracleWMSSession,
        OracleWMSSetup,
        OracleWMSShield,
        OracleWMSSignature,
        OracleWMSSingle,
        OracleWMSSize,
        OracleWMSSolo,
        OracleWMSSort,
        OracleWMSSpan,
        OracleWMSSpecial,
        OracleWMSSpecific,
        OracleWMSStability,
        OracleWMSStack,
        OracleWMSStage,
        OracleWMSStandalone,
        OracleWMSStandard,
        OracleWMSStatement,
        OracleWMSStep,
        OracleWMSStorage,
        OracleWMSString,
        OracleWMSStuff,
        OracleWMSSubject,
        OracleWMSSubstance,
        OracleWMSSuitable,
        OracleWMSSum,
        OracleWMSSupport,
        OracleWMSSynchronization,
        OracleWMSThickness,
        OracleWMSThing,
        OracleWMSThreshold,
        OracleWMSTotal,
        OracleWMSTransaction,
        OracleWMSTransport,
        OracleWMSTube,
        OracleWMSTuning,
        OracleWMSTypical,
        OracleWMSUnderstanding,
        OracleWMSUniform,
        OracleWMSUnique,
        OracleWMSUniversal,
        OracleWMSUpdate,
        OracleWMSUpgrade,
        OracleWMSUser,
        OracleWMSUsual,
        OracleWMSValidation,
        OracleWMSVariant,
        OracleWMSVehicle,
        OracleWMSVerification,
        OracleWMSVersion,
        OracleWMSVessel,
        OracleWMSVolume,
        OracleWMSWall,
        OracleWMSWarehouse,
        OracleWMSWarranty,
        OracleWMSWhole,
        OracleWMSWidth,
        OracleWMSWire,
        OracleWMSWisdom,
        OracleWMSWorkflow,
        OracleWMSWorkProduct,
    )

# ==============================================================================
# DBT ORACLE WMS DOMAIN TYPES - Python 3.13 Enhanced
# ==============================================================================

# DBT Oracle WMS project domain types
DBTOracleWMSProjectName = Annotated[
    str, Field(min_length=1, max_length=100, description="DBT Oracle WMS project name")
]
DBTOracleWMSProjectPath = Annotated[
    str, Field(min_length=1, max_length=500, description="DBT Oracle WMS project path")
]
DBTOracleWMSProjectDescription = Annotated[
    str,
    Field(
        min_length=1, max_length=1000, description="DBT Oracle WMS project description"
    ),
]

# DBT Oracle WMS model domain types
DBTOracleWMSModelPath = Annotated[
    str, Field(min_length=1, max_length=500, description="DBT Oracle WMS model path")
]
DBTOracleWMSModelDescription = Annotated[
    str,
    Field(
        min_length=1, max_length=1000, description="DBT Oracle WMS model description"
    ),
]
DBTOracleWMSModelSQL = Annotated[
    str, Field(min_length=1, max_length=100000, description="DBT Oracle WMS model SQL")
]

# DBT Oracle WMS source domain types
DBTOracleWMSSourceDescription = Annotated[
    str,
    Field(
        min_length=1, max_length=1000, description="DBT Oracle WMS source description"
    ),
]
DBTOracleWMSSourceTableName = Annotated[
    str,
    Field(min_length=1, max_length=100, description="DBT Oracle WMS source table name"),
]
DBTOracleWMSSourceSchemaName = Annotated[
    str,
    Field(
        min_length=1, max_length=100, description="DBT Oracle WMS source schema name"
    ),
]

# DBT Oracle WMS test domain types
DBTOracleWMSTestDescription = Annotated[
    str,
    Field(min_length=1, max_length=1000, description="DBT Oracle WMS test description"),
]
DBTOracleWMSTestSQL = Annotated[
    str, Field(min_length=1, max_length=100000, description="DBT Oracle WMS test SQL")
]
DBTOracleWMSTestType = Literal[
    "not_null",
    "unique",
    "accepted_values",
    "relationships",
    "expression",
    "schema",
    "data",
]

# DBT Oracle WMS macro domain types
DBTOracleWMSMacroDescription = Annotated[
    str,
    Field(
        min_length=1, max_length=1000, description="DBT Oracle WMS macro description"
    ),
]
DBTOracleWMSMacroSQL = Annotated[
    str, Field(min_length=1, max_length=100000, description="DBT Oracle WMS macro SQL")
]
DBTOracleWMSMacroArgument = Annotated[
    str,
    Field(min_length=1, max_length=100, description="DBT Oracle WMS macro argument"),
]

# DBT Oracle WMS snapshot domain types
DBTOracleWMSSnapshotDescription = Annotated[
    str,
    Field(
        min_length=1, max_length=1000, description="DBT Oracle WMS snapshot description"
    ),
]
DBTOracleWMSSnapshotSQL = Annotated[
    str,
    Field(min_length=1, max_length=100000, description="DBT Oracle WMS snapshot SQL"),
]
DBTOracleWMSSnapshotStrategy = Literal["timestamp", "check", "hash"]

# DBT Oracle WMS analysis domain types
DBTOracleWMSAnalysisDescription = Annotated[
    str,
    Field(
        min_length=1, max_length=1000, description="DBT Oracle WMS analysis description"
    ),
]
DBTOracleWMSAnalysisSQL = Annotated[
    str,
    Field(min_length=1, max_length=100000, description="DBT Oracle WMS analysis SQL"),
]
DBTOracleWMSAnalysisType = Literal[
    "exploratory", "validation", "diagnostic", "predictive"
]

# DBT Oracle WMS compilation domain types
DBTOracleWMSCompilationStatus = Literal[
    "pending", "running", "completed", "failed", "skipped"
]
DBTOracleWMSCompilationMessage = Annotated[
    str,
    Field(
        min_length=1, max_length=10000, description="DBT Oracle WMS compilation message"
    ),
]
DBTOracleWMSCompilationError = Annotated[
    str,
    Field(
        min_length=1, max_length=10000, description="DBT Oracle WMS compilation error"
    ),
]

# DBT Oracle WMS execution domain types
DBTOracleWMSExecutionStatus = Literal[
    "pending", "running", "completed", "failed", "skipped"
]
DBTOracleWMSExecutionMessage = Annotated[
    str,
    Field(
        min_length=1, max_length=10000, description="DBT Oracle WMS execution message"
    ),
]
DBTOracleWMSExecutionError = Annotated[
    str,
    Field(min_length=1, max_length=10000, description="DBT Oracle WMS execution error"),
]

# DBT Oracle WMS documentation domain types
DBTOracleWMSDocumentationDescription = Annotated[
    str,
    Field(
        min_length=1,
        max_length=10000,
        description="DBT Oracle WMS documentation description",
    ),
]
DBTOracleWMSDocumentationFormat = Literal["markdown", "html", "json", "yaml"]
DBTOracleWMSDocumentationType = Literal[
    "model", "source", "test", "macro", "snapshot", "analysis"
]

# DBT Oracle WMS timeout types
DBTOracleWMSProjectTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSModelTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSSourceTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSTestTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSMacroTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSSnapshotTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSAnalysisTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSCompilationTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSExecutionTimeout = TimeoutSeconds  # Alias for clarity
DBTOracleWMSDocumentationTimeout = TimeoutSeconds  # Alias for clarity

# DBT Oracle WMS retry types
DBTOracleWMSProjectRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS project retry attempts")
]
DBTOracleWMSModelRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS model retry attempts")
]
DBTOracleWMSSourceRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS source retry attempts")
]
DBTOracleWMSTestRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS test retry attempts")
]
DBTOracleWMSMacroRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS macro retry attempts")
]
DBTOracleWMSSnapshotRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS snapshot retry attempts")
]
DBTOracleWMSAnalysisRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS analysis retry attempts")
]
DBTOracleWMSCompilationRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS compilation retry attempts")
]
DBTOracleWMSExecutionRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS execution retry attempts")
]
DBTOracleWMSDocumentationRetries = Annotated[
    int, Field(ge=0, le=10, description="DBT Oracle WMS documentation retry attempts")
]

# DBT Oracle WMS parallelism types
DBTOracleWMSProjectParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS project parallelism")
]
DBTOracleWMSModelParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS model parallelism")
]
DBTOracleWMSSourceParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS source parallelism")
]
DBTOracleWMSTestParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS test parallelism")
]
DBTOracleWMSMacroParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS macro parallelism")
]
DBTOracleWMSSnapshotParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS snapshot parallelism")
]
DBTOracleWMSAnalysisParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS analysis parallelism")
]
DBTOracleWMSCompilationParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS compilation parallelism")
]
DBTOracleWMSExecutionParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS execution parallelism")
]
DBTOracleWMSDocumentationParallelism = Annotated[
    int, Field(ge=1, le=100, description="DBT Oracle WMS documentation parallelism")
]

# ==============================================================================
# DBT ORACLE WMS DOMAIN TYPEDDICTS
# ==============================================================================


class DBTOracleWMSProject(TypedDict):
    """DBT Oracle WMS project domain structure using flext-core types."""

    # Project identification
    project_id: DBTRunId
    project_name: DBTOracleWMSProjectName
    project_path: DBTOracleWMSProjectPath
    project_description: DBTOracleWMSProjectDescription

    # Project metadata
    version: Version
    environment: Environment
    created_at: Timestamp
    updated_at: Timestamp

    # Project configuration
    dbt_version: Version
    oracle_wms_version: Version
    flext_core_version: Version

    # Project settings
    enabled: bool
    debug: bool
    log_level: LogLevel

    # Project resources
    models: list[DBTModelId]
    sources: list[DBTSourceId]
    tests: list[DBTTestId]
    macros: list[DBTMacroId]
    snapshots: list[DBTSnapshotId]
    analyses: list[DBTAnalysisId]

    # Project performance
    compilation_timeout: DBTOracleWMSProjectTimeout
    execution_timeout: DBTOracleWMSProjectTimeout
    retry_attempts: DBTOracleWMSProjectRetries
    parallelism: DBTOracleWMSProjectParallelism

    # Project Oracle WMS integration
    oracle_wms_connection: OracleWMSConnectionId
    oracle_wms_entities: list[OracleWMSEntityType]
    oracle_wms_schemas: list[OracleWMSSchemaId]
    oracle_wms_operations: list[OracleWMSOperationId]

    # Project monitoring
    monitoring_enabled: bool
    observability_enabled: bool
    metrics_collection: bool
    health_checks: bool


class DBTOracleWMSModel(TypedDict):
    """DBT Oracle WMS model domain structure using flext-core types."""

    # Model identification
    model_id: DBTModelId
    model_name: DBTModelName
    model_path: DBTOracleWMSModelPath
    model_description: DBTOracleWMSModelDescription

    # Model metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_compiled: Timestamp | None
    last_executed: Timestamp | None

    # Model configuration
    materialization: DBTMaterialization
    schema: DBTSchemaName
    database: DBTDatabaseName
    table_name: DBTTableName

    # Model SQL
    raw_sql: DBTOracleWMSModelSQL
    compiled_sql: DBTOracleWMSModelSQL | None

    # Model dependencies
    depends_on_models: list[DBTModelId]
    depends_on_sources: list[DBTSourceId]
    depends_on_macros: list[DBTMacroId]

    # Model performance
    compilation_timeout: DBTOracleWMSModelTimeout
    execution_timeout: DBTOracleWMSModelTimeout
    retry_attempts: DBTOracleWMSModelRetries
    parallelism: DBTOracleWMSModelParallelism

    # Model Oracle WMS integration
    oracle_wms_entities: list[OracleWMSEntityType]
    oracle_wms_fields: list[WMSFieldName]
    oracle_wms_filters: list[WMSFilterId]
    oracle_wms_sorts: list[WMSOrderValue]

    # Model validation
    tests: list[DBTTestId]
    validation_enabled: bool
    validation_rules: list[str]

    # Model documentation
    documentation: DBTOracleWMSDocumentationDescription | None
    tags: list[str]
    meta: dict[str, str]


class DBTOracleWMSSource(TypedDict):
    """DBT Oracle WMS source domain structure using flext-core types."""

    # Source identification
    source_id: DBTSourceId
    source_name: DBTSourceName
    source_description: DBTOracleWMSSourceDescription

    # Source metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_refreshed: Timestamp | None

    # Source configuration
    database: DBTDatabaseName
    schema: DBTOracleWMSSourceSchemaName
    table_name: DBTOracleWMSSourceTableName

    # Source Oracle WMS integration
    oracle_wms_entity: OracleWMSEntityType
    oracle_wms_connection: OracleWMSConnectionId
    oracle_wms_schema: OracleWMSSchemaId
    oracle_wms_query: OracleWMSQueryId

    # Source freshness
    freshness_enabled: bool
    freshness_warn_after: TimeoutSeconds | None
    freshness_error_after: TimeoutSeconds | None
    loaded_at_field: WMSFieldName | None

    # Source performance
    refresh_timeout: DBTOracleWMSSourceTimeout
    retry_attempts: DBTOracleWMSSourceRetries
    parallelism: DBTOracleWMSSourceParallelism

    # Source validation
    tests: list[DBTTestId]
    validation_enabled: bool
    validation_rules: list[str]

    # Source documentation
    documentation: DBTOracleWMSDocumentationDescription | None
    tags: list[str]
    meta: dict[str, str]


class DBTOracleWMSTest(TypedDict):
    """DBT Oracle WMS test domain structure using flext-core types."""

    # Test identification
    test_id: DBTTestId
    test_name: DBTTestName
    test_description: DBTOracleWMSTestDescription
    test_type: DBTOracleWMSTestType

    # Test metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_executed: Timestamp | None

    # Test configuration
    model_id: DBTModelId | None
    source_id: DBTSourceId | None
    column_name: WMSFieldName | None

    # Test SQL
    test_sql: DBTOracleWMSTestSQL
    compiled_sql: DBTOracleWMSTestSQL | None

    # Test execution
    execution_status: DBTOracleWMSExecutionStatus
    execution_message: DBTOracleWMSExecutionMessage | None
    execution_error: DBTOracleWMSExecutionError | None

    # Test performance
    execution_timeout: DBTOracleWMSTestTimeout
    retry_attempts: DBTOracleWMSTestRetries
    parallelism: DBTOracleWMSTestParallelism

    # Test Oracle WMS integration
    oracle_wms_entities: list[OracleWMSEntityType]
    oracle_wms_fields: list[WMSFieldName]
    oracle_wms_validations: list[WMSFilterId]

    # Test severity
    severity: Literal["error", "warn", "info"]
    fail_calc: Literal["count", "percentage"]

    # Test documentation
    documentation: DBTOracleWMSDocumentationDescription | None
    tags: list[str]
    meta: dict[str, str]


class DBTOracleWMSMacro(TypedDict):
    """DBT Oracle WMS macro domain structure using flext-core types."""

    # Macro identification
    macro_id: DBTMacroId
    macro_name: DBTMacroName
    macro_description: DBTOracleWMSMacroDescription

    # Macro metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_compiled: Timestamp | None

    # Macro configuration
    macro_type: Literal["function", "operation", "test", "materialization"]
    arguments: list[DBTOracleWMSMacroArgument]

    # Macro SQL
    macro_sql: DBTOracleWMSMacroSQL
    compiled_sql: DBTOracleWMSMacroSQL | None

    # Macro dependencies
    depends_on_macros: list[DBTMacroId]
    used_by_models: list[DBTModelId]
    used_by_tests: list[DBTTestId]

    # Macro performance
    compilation_timeout: DBTOracleWMSMacroTimeout
    retry_attempts: DBTOracleWMSMacroRetries
    parallelism: DBTOracleWMSMacroParallelism

    # Macro Oracle WMS integration
    oracle_wms_operations: list[OracleWMSOperationId]
    oracle_wms_transformations: list[str]
    oracle_wms_validations: list[str]

    # Macro documentation
    documentation: DBTOracleWMSDocumentationDescription | None
    tags: list[str]
    meta: dict[str, str]


class DBTOracleWMSSnapshot(TypedDict):
    """DBT Oracle WMS snapshot domain structure using flext-core types."""

    # Snapshot identification
    snapshot_id: DBTSnapshotId
    snapshot_name: DBTSnapshotName
    snapshot_description: DBTOracleWMSSnapshotDescription

    # Snapshot metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_executed: Timestamp | None

    # Snapshot configuration
    target_database: DBTDatabaseName
    target_schema: DBTSchemaName
    target_table: DBTTableName

    # Snapshot strategy
    strategy: DBTOracleWMSSnapshotStrategy
    unique_key: WMSFieldName
    updated_at_field: WMSFieldName | None
    check_cols: list[WMSFieldName] | None

    # Snapshot SQL
    snapshot_sql: DBTOracleWMSSnapshotSQL
    compiled_sql: DBTOracleWMSSnapshotSQL | None

    # Snapshot dependencies
    depends_on_models: list[DBTModelId]
    depends_on_sources: list[DBTSourceId]
    depends_on_macros: list[DBTMacroId]

    # Snapshot performance
    execution_timeout: DBTOracleWMSSnapshotTimeout
    retry_attempts: DBTOracleWMSSnapshotRetries
    parallelism: DBTOracleWMSSnapshotParallelism

    # Snapshot Oracle WMS integration
    oracle_wms_entity: OracleWMSEntityType
    oracle_wms_connection: OracleWMSConnectionId
    oracle_wms_schema: OracleWMSSchemaId
    oracle_wms_query: OracleWMSQueryId

    # Snapshot validation
    tests: list[DBTTestId]
    validation_enabled: bool
    validation_rules: list[str]

    # Snapshot documentation
    documentation: DBTOracleWMSDocumentationDescription | None
    tags: list[str]
    meta: dict[str, str]


class DBTOracleWMSAnalysis(TypedDict):
    """DBT Oracle WMS analysis domain structure using flext-core types."""

    # Analysis identification
    analysis_id: DBTAnalysisId
    analysis_name: DBTAnalysisName
    analysis_description: DBTOracleWMSAnalysisDescription
    analysis_type: DBTOracleWMSAnalysisType

    # Analysis metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_executed: Timestamp | None

    # Analysis configuration
    target_database: DBTDatabaseName
    target_schema: DBTSchemaName

    # Analysis SQL
    analysis_sql: DBTOracleWMSAnalysisSQL
    compiled_sql: DBTOracleWMSAnalysisSQL | None

    # Analysis dependencies
    depends_on_models: list[DBTModelId]
    depends_on_sources: list[DBTSourceId]
    depends_on_macros: list[DBTMacroId]

    # Analysis performance
    execution_timeout: DBTOracleWMSAnalysisTimeout
    retry_attempts: DBTOracleWMSAnalysisRetries
    parallelism: DBTOracleWMSAnalysisParallelism

    # Analysis Oracle WMS integration
    oracle_wms_entities: list[OracleWMSEntityType]
    oracle_wms_metrics: list[str]
    oracle_wms_dimensions: list[str]
    oracle_wms_filters: list[WMSFilterId]

    # Analysis results
    results_format: Literal["table", "chart", "report", "dashboard"]
    results_retention: PositiveInt
    results_path: FilePath | None

    # Analysis documentation
    documentation: DBTOracleWMSDocumentationDescription | None
    tags: list[str]
    meta: dict[str, str]


class DBTOracleWMSCompilation(TypedDict):
    """DBT Oracle WMS compilation domain structure using flext-core types."""

    # Compilation identification
    compilation_id: DBTCompilationId
    compilation_name: str

    # Compilation metadata
    started_at: Timestamp
    completed_at: Timestamp | None
    duration_seconds: float | None

    # Compilation targets
    project_id: DBTRunId
    models: list[DBTModelId]
    sources: list[DBTSourceId]
    tests: list[DBTTestId]
    macros: list[DBTMacroId]
    snapshots: list[DBTSnapshotId]
    analyses: list[DBTAnalysisId]

    # Compilation status
    status: DBTOracleWMSCompilationStatus
    message: DBTOracleWMSCompilationMessage | None
    error: DBTOracleWMSCompilationError | None

    # Compilation performance
    timeout: DBTOracleWMSCompilationTimeout
    retry_attempts: DBTOracleWMSCompilationRetries
    parallelism: DBTOracleWMSCompilationParallelism

    # Compilation Oracle WMS integration
    oracle_wms_connections: list[OracleWMSConnectionId]
    oracle_wms_schemas: list[OracleWMSSchemaId]
    oracle_wms_entities: list[OracleWMSEntityType]

    # Compilation artifacts
    compiled_models: dict[DBTModelId, str]
    compiled_tests: dict[DBTTestId, str]
    compiled_macros: dict[DBTMacroId, str]
    compiled_snapshots: dict[DBTSnapshotId, str]
    compiled_analyses: dict[DBTAnalysisId, str]

    # Compilation statistics
    models_compiled: NonNegativeInt
    tests_compiled: NonNegativeInt
    macros_compiled: NonNegativeInt
    snapshots_compiled: NonNegativeInt
    analyses_compiled: NonNegativeInt

    # Compilation warnings
    warnings: list[str]
    deprecations: list[str]


class DBTOracleWMSExecution(TypedDict):
    """DBT Oracle WMS execution domain structure using flext-core types."""

    # Execution identification
    execution_id: DBTExecutionId
    execution_name: str

    # Execution metadata
    started_at: Timestamp
    completed_at: Timestamp | None
    duration_seconds: float | None

    # Execution targets
    project_id: DBTRunId
    models: list[DBTModelId]
    tests: list[DBTTestId]
    snapshots: list[DBTSnapshotId]
    analyses: list[DBTAnalysisId]

    # Execution status
    status: DBTOracleWMSExecutionStatus
    message: DBTOracleWMSExecutionMessage | None
    error: DBTOracleWMSExecutionError | None

    # Execution performance
    timeout: DBTOracleWMSExecutionTimeout
    retry_attempts: DBTOracleWMSExecutionRetries
    parallelism: DBTOracleWMSExecutionParallelism

    # Execution Oracle WMS integration
    oracle_wms_connections: list[OracleWMSConnectionId]
    oracle_wms_operations: list[OracleWMSOperationId]
    oracle_wms_transactions: list[WMSTransactionId]

    # Execution results
    models_executed: NonNegativeInt
    tests_executed: NonNegativeInt
    snapshots_executed: NonNegativeInt
    analyses_executed: NonNegativeInt

    # Execution statistics
    models_passed: NonNegativeInt
    models_failed: NonNegativeInt
    tests_passed: NonNegativeInt
    tests_failed: NonNegativeInt
    snapshots_passed: NonNegativeInt
    snapshots_failed: NonNegativeInt
    analyses_passed: NonNegativeInt
    analyses_failed: NonNegativeInt

    # Execution artifacts
    execution_logs: list[str]
    execution_metrics: dict[str, float]
    execution_reports: list[FilePath]


class DBTOracleWMSDocumentation(TypedDict):
    """DBT Oracle WMS documentation domain structure using flext-core types."""

    # Documentation identification
    documentation_id: DBTDocumentationId
    documentation_name: DBTDocumentationName
    documentation_type: DBTOracleWMSDocumentationType

    # Documentation metadata
    version: Version
    created_at: Timestamp
    updated_at: Timestamp
    last_generated: Timestamp | None

    # Documentation content
    description: DBTOracleWMSDocumentationDescription
    format: DBTOracleWMSDocumentationFormat
    content: str

    # Documentation targets
    project_id: DBTRunId | None
    model_id: DBTModelId | None
    source_id: DBTSourceId | None
    test_id: DBTTestId | None
    macro_id: DBTMacroId | None
    snapshot_id: DBTSnapshotId | None
    analysis_id: DBTAnalysisId | None

    # Documentation Oracle WMS integration
    oracle_wms_entities: list[OracleWMSEntityType]
    oracle_wms_fields: list[WMSFieldName]
    oracle_wms_operations: list[OracleWMSOperationId]

    # Documentation generation
    generation_timeout: DBTOracleWMSDocumentationTimeout
    retry_attempts: DBTOracleWMSDocumentationRetries
    parallelism: DBTOracleWMSDocumentationParallelism

    # Documentation output
    output_path: FilePath | None
    output_format: list[DBTOracleWMSDocumentationFormat]
    output_enabled: bool

    # Documentation metadata
    tags: list[str]
    meta: dict[str, str]
    authors: list[str]
    reviewers: list[str]


# ==============================================================================
# TYPE ALIASES FOR MAXIMUM CODE REDUCTION
# ==============================================================================

# Project configuration aggregates
type DBTOracleWMSProjectConfiguration = DBTOracleWMSProject
type DBTOracleWMSModelConfiguration = DBTOracleWMSModel
type DBTOracleWMSSourceConfiguration = DBTOracleWMSSource

# Test and validation aggregates
type DBTOracleWMSTestConfiguration = DBTOracleWMSTest
type DBTOracleWMSMacroConfiguration = DBTOracleWMSMacro
type DBTOracleWMSSnapshotConfiguration = DBTOracleWMSSnapshot

# Analysis and documentation aggregates
type DBTOracleWMSAnalysisConfiguration = DBTOracleWMSAnalysis
type DBTOracleWMSCompilationConfiguration = DBTOracleWMSCompilation
type DBTOracleWMSExecutionConfiguration = DBTOracleWMSExecution
type DBTOracleWMSDocumentationConfiguration = DBTOracleWMSDocumentation

# ==============================================================================
# EXPORT PUBLIC API
# ==============================================================================

__all__ = [
    # Core flext-core types (re-exported)
    "URL",
    "ConfigurationKey",
    "ConfigurationValue",
    "ConnectionTimeout",
    "CpuPercent",
    "DBTAnalysisId",
    "DBTAnalysisName",
    "DBTCompilationId",
    "DBTDatabaseName",
    "DBTDocumentationId",
    "DBTDocumentationName",
    "DBTExecutionId",
    "DBTMacroId",
    "DBTMacroName",
    "DBTMaterialization",
    "DBTModelId",
    "DBTModelName",
    "DBTOracleWMSAnalysis",
    "DBTOracleWMSAnalysisConfiguration",
    "DBTOracleWMSAnalysisDescription",
    "DBTOracleWMSAnalysisParallelism",
    "DBTOracleWMSAnalysisRetries",
    "DBTOracleWMSAnalysisSQL",
    "DBTOracleWMSAnalysisTimeout",
    "DBTOracleWMSAnalysisType",
    "DBTOracleWMSCompilation",
    "DBTOracleWMSCompilationConfiguration",
    "DBTOracleWMSCompilationError",
    "DBTOracleWMSCompilationMessage",
    "DBTOracleWMSCompilationParallelism",
    "DBTOracleWMSCompilationRetries",
    "DBTOracleWMSCompilationStatus",
    "DBTOracleWMSCompilationTimeout",
    "DBTOracleWMSDocumentation",
    "DBTOracleWMSDocumentationConfiguration",
    "DBTOracleWMSDocumentationDescription",
    "DBTOracleWMSDocumentationFormat",
    "DBTOracleWMSDocumentationParallelism",
    "DBTOracleWMSDocumentationRetries",
    "DBTOracleWMSDocumentationTimeout",
    "DBTOracleWMSDocumentationType",
    "DBTOracleWMSExecution",
    "DBTOracleWMSExecutionConfiguration",
    "DBTOracleWMSExecutionError",
    "DBTOracleWMSExecutionMessage",
    "DBTOracleWMSExecutionParallelism",
    "DBTOracleWMSExecutionRetries",
    "DBTOracleWMSExecutionStatus",
    "DBTOracleWMSExecutionTimeout",
    "DBTOracleWMSMacro",
    "DBTOracleWMSMacroArgument",
    "DBTOracleWMSMacroConfiguration",
    "DBTOracleWMSMacroDescription",
    "DBTOracleWMSMacroParallelism",
    "DBTOracleWMSMacroRetries",
    "DBTOracleWMSMacroSQL",
    "DBTOracleWMSMacroTimeout",
    "DBTOracleWMSModel",
    "DBTOracleWMSModelConfiguration",
    "DBTOracleWMSModelDescription",
    "DBTOracleWMSModelParallelism",
    "DBTOracleWMSModelPath",
    "DBTOracleWMSModelRetries",
    "DBTOracleWMSModelSQL",
    "DBTOracleWMSModelTimeout",
    # Domain structures
    "DBTOracleWMSProject",
    # Type aliases
    "DBTOracleWMSProjectConfiguration",
    "DBTOracleWMSProjectDescription",
    # DBT Oracle WMS domain-specific types
    "DBTOracleWMSProjectName",
    # Parallelism types
    "DBTOracleWMSProjectParallelism",
    "DBTOracleWMSProjectPath",
    # Retry types
    "DBTOracleWMSProjectRetries",
    # Timeout types
    "DBTOracleWMSProjectTimeout",
    "DBTOracleWMSSnapshot",
    "DBTOracleWMSSnapshotConfiguration",
    "DBTOracleWMSSnapshotDescription",
    "DBTOracleWMSSnapshotParallelism",
    "DBTOracleWMSSnapshotRetries",
    "DBTOracleWMSSnapshotSQL",
    "DBTOracleWMSSnapshotStrategy",
    "DBTOracleWMSSnapshotTimeout",
    "DBTOracleWMSSource",
    "DBTOracleWMSSourceConfiguration",
    "DBTOracleWMSSourceDescription",
    "DBTOracleWMSSourceParallelism",
    "DBTOracleWMSSourceRetries",
    "DBTOracleWMSSourceSchemaName",
    "DBTOracleWMSSourceTableName",
    "DBTOracleWMSSourceTimeout",
    "DBTOracleWMSTest",
    "DBTOracleWMSTestConfiguration",
    "DBTOracleWMSTestDescription",
    "DBTOracleWMSTestParallelism",
    "DBTOracleWMSTestRetries",
    "DBTOracleWMSTestSQL",
    "DBTOracleWMSTestTimeout",
    "DBTOracleWMSTestType",
    "DBTRunId",
    "DBTSchemaName",
    "DBTSnapshotId",
    "DBTSnapshotName",
    "DBTSourceId",
    "DBTSourceName",
    "DBTTableName",
    "DBTTestId",
    "DBTTestName",
    "DBTThreadCount",
    "DatabaseName",
    "DatabaseURL",
    "DirPath",
    "DiskMB",
    "EntityId",
    "Environment",
    "FileName",
    "FilePath",
    "FileSize",
    "Json",
    "JsonList",
    "JsonSchema",
    "LogLevel",
    "MemoryMB",
    "NonEmptyStr",
    "NonNegativeInt",
    "PositiveInt",
    "ProjectName",
    "ServiceResult",
    "StrEnum",
    "TimeoutSeconds",
    "Timestamp",
    "Version",
]
