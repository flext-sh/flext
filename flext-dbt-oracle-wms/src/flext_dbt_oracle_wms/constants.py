"""FLEXT DBT Oracle WMS Constants - Simplified version.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from typing import Final


# DBT Oracle WMS Entity Types
class DBTOracleWMSEntityTypes:
    """Oracle WMS entity types for DBT models."""
    
    ALLOCATION: Final[str] = "allocation"
    ORDER_HDR: Final[str] = "order_hdr"
    ORDER_DTL: Final[str] = "order_dtl"
    INVENTORY: Final[str] = "inventory"
    LOCATION: Final[str] = "location"
    ITEM: Final[str] = "item"
    SHIPMENT: Final[str] = "shipment"
    RECEIPT: Final[str] = "receipt"
    TASK: Final[str] = "task"
    WAVE: Final[str] = "wave"


# DBT Materialization Types
class DBTOracleWMSMaterializations:
    """DBT materialization types for Oracle WMS."""
    
    TABLE: Final[str] = "table"
    VIEW: Final[str] = "view"
    INCREMENTAL: Final[str] = "incremental"
    SNAPSHOT: Final[str] = "snapshot"
    EPHEMERAL: Final[str] = "ephemeral"


# DBT Test Types
class DBTOracleWMSTestTypes:
    """DBT test types for Oracle WMS."""
    
    UNIQUE: Final[str] = "unique"
    NOT_NULL: Final[str] = "not_null"
    RELATIONSHIPS: Final[str] = "relationships"
    ACCEPTED_VALUES: Final[str] = "accepted_values"
    DATA_QUALITY: Final[str] = "data_quality"


# DBT Macro Types
class DBTOracleWMSMacroTypes:
    """DBT macro types for Oracle WMS."""
    
    UTILITY: Final[str] = "utility"
    TRANSFORMATION: Final[str] = "transformation"
    AUDIT: Final[str] = "audit"
    ORACLE_SPECIFIC: Final[str] = "oracle_specific"


# DBT Documentation Types
class DBTOracleWMSDocumentationTypes:
    """DBT documentation types for Oracle WMS."""
    
    MODEL: Final[str] = "model"
    SOURCE: Final[str] = "source"
    MACRO: Final[str] = "macro"
    ANALYSIS: Final[str] = "analysis"


# DBT Defaults
class DBTOracleWMSDefaults:
    """Default values for DBT Oracle WMS."""
    
    PROJECT_NAME: Final[str] = "flext_dbt_oracle_wms"
    VERSION: Final[str] = "2.0.0"
    PROFILE: Final[str] = "flext_oracle_wms"
    SCHEMA_PREFIX: Final[str] = "wms"
    BATCH_SIZE: Final[int] = 1000
    INCREMENTAL_LOOKBACK_DAYS: Final[int] = 7
    DATA_QUALITY_THRESHOLD: Final[float] = 0.95
    # Database constants
    DatabaseName,
    DBTAnalysisName,
    # DBT constants
    DBTDatabaseName,
    DBTDocumentationName,
    DBTMacroName,
    DBTMaterialization,
    DBTModelName,
    DBTSchemaName,
    DBTSnapshotName,
    DBTSourceName,
    DBTTableName,
    DBTTestName,
    NonEmptyStr,
    NonNegativeInt,
    OracleWMSApiVersion,
    OracleWMSAuthMethod,
    # Oracle WMS constants
    OracleWMSEntityType,
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
    WMSFilterLevel,
    WMSFilterOperator,
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
    WMSOneLevel,
    WMSOnlyLevel,
    WMSOpenLevel,
    WMSOperationalLevel,
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
    WMSParameterLevel,
    WMSParticularLevel,
    WMSPartitionLevel,
    WMSPartLevel,
    WMSPartnershipLevel,
    WMSPassLevel,
    WMSPasswordLevel,
    WMSPatternLevel,
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
    WMSSchemaLevel,
    WMSScopeLevel,
    WMSSealLevel,
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
    WMSUpdateLevel,
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
    from flext_dbt_oracle_wms.domain.types import (
        DBTOracleWMSAnalysisDescription,
        DBTOracleWMSAnalysisSQL,
        DBTOracleWMSAnalysisType,
        DBTOracleWMSCompilationError,
        DBTOracleWMSCompilationMessage,
        DBTOracleWMSCompilationStatus,
        DBTOracleWMSDocumentationDescription,
        DBTOracleWMSDocumentationFormat,
        DBTOracleWMSDocumentationType,
        DBTOracleWMSExecutionError,
        DBTOracleWMSExecutionMessage,
        DBTOracleWMSExecutionStatus,
        DBTOracleWMSMacroArgument,
        DBTOracleWMSMacroDescription,
        DBTOracleWMSMacroSQL,
        DBTOracleWMSModelDescription,
        DBTOracleWMSModelPath,
        DBTOracleWMSModelSQL,
        DBTOracleWMSProjectDescription,
        # DBT Oracle WMS domain types
        DBTOracleWMSProjectName,
        DBTOracleWMSProjectPath,
        DBTOracleWMSSnapshotDescription,
        DBTOracleWMSSnapshotSQL,
        DBTOracleWMSSnapshotStrategy,
        DBTOracleWMSSourceDescription,
        DBTOracleWMSSourceSchemaName,
        DBTOracleWMSSourceTableName,
        DBTOracleWMSTestDescription,
        DBTOracleWMSTestSQL,
        DBTOracleWMSTestType,
    )

# ==============================================================================
# DBT ORACLE WMS DEFAULTS - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleWMSDefaults(StrEnum):
    """DBT Oracle WMS default values using flext-core types."""

    # Default project configuration
    PROJECT_NAME = "dbt_oracle_wms_project"
    PROJECT_VERSION = "1.0.0"
    PROJECT_DESCRIPTION = "DBT Oracle WMS data transformation project"

    # Default DBT configuration
    DBT_VERSION = "1.8.0"
    DBT_THREADS = "4"
    DBT_TARGET = "default"
    DBT_PROFILE = "oracle_wms"

    # Default Oracle WMS configuration
    ORACLE_WMS_API_VERSION = "v1"
    ORACLE_WMS_AUTH_METHOD = "basic"
    ORACLE_WMS_COMPANY_CODE = "DEFAULT"
    ORACLE_WMS_FACILITY_CODE = "MAIN"
    ORACLE_WMS_BASE_URL = "https://oracle-wms.example.com/api"

    # Default connection settings
    CONNECTION_TIMEOUT = "30"
    CONNECTION_RETRIES = "3"
    CONNECTION_PARALLELISM = "4"
    CONNECTION_POOL_SIZE = "10"

    # Default query settings
    QUERY_TIMEOUT = "300"
    QUERY_RETRIES = "3"
    QUERY_PARALLELISM = "4"
    QUERY_BATCH_SIZE = "1000"

    # Default compilation settings
    COMPILATION_TIMEOUT = "600"
    COMPILATION_RETRIES = "3"
    COMPILATION_PARALLELISM = "4"
    COMPILATION_MEMORY_MB = "1024"

    # Default execution settings
    EXECUTION_TIMEOUT = "3600"
    EXECUTION_RETRIES = "3"
    EXECUTION_PARALLELISM = "4"
    EXECUTION_MEMORY_MB = "2048"

    # Default test settings
    TEST_TIMEOUT = "300"
    TEST_RETRIES = "3"
    TEST_PARALLELISM = "4"
    TEST_SEVERITY = "error"

    # Default documentation settings
    DOCUMENTATION_TIMEOUT = "300"
    DOCUMENTATION_RETRIES = "3"
    DOCUMENTATION_PARALLELISM = "4"
    DOCUMENTATION_FORMAT = "markdown"

    # Default materialization settings
    MATERIALIZATION = "table"
    MATERIALIZATION_STRATEGY = "full_refresh"
    MATERIALIZATION_PARALLELISM = "4"

    # Default cache settings
    CACHE_ENABLED = "true"
    CACHE_TTL_SECONDS = "3600"
    CACHE_MAX_SIZE = "1000"
    CACHE_COMPRESSION = "true"

    # Default logging settings
    LOG_LEVEL = "INFO"
    LOG_ENABLED = "true"
    LOG_RETENTION_DAYS = "30"

    # Default monitoring settings
    MONITORING_ENABLED = "true"
    METRICS_ENABLED = "true"
    METRICS_RETENTION_DAYS = "90"
    HEALTH_CHECKS_ENABLED = "true"

    # Default security settings
    SECURITY_ENABLED = "true"
    ENCRYPTION_ENABLED = "true"
    SSL_ENABLED = "true"
    SSL_VERIFY = "true"

    # Default backup settings
    BACKUP_ENABLED = "true"
    BACKUP_RETENTION_DAYS = "90"
    BACKUP_COMPRESSION = "true"

    # Default Oracle WMS entity settings
    ENTITY_DISCOVERY_ENABLED = "true"
    ENTITY_REFRESH_INTERVAL = "3600"
    ENTITY_CACHE_TTL = "1800"
    ENTITY_VALIDATION_ENABLED = "true"

    # Default schema settings
    SCHEMA_DISCOVERY_ENABLED = "true"
    SCHEMA_REFRESH_INTERVAL = "3600"
    SCHEMA_CACHE_TTL = "1800"
    SCHEMA_VALIDATION_ENABLED = "true"

    # Default filtering settings
    FILTER_ENABLED = "true"
    FILTER_PARALLELISM = "4"
    FILTER_CACHE_ENABLED = "true"

    # Default flattening settings
    FLATTENING_ENABLED = "true"
    FLATTENING_DEPTH = "10"
    FLATTENING_SEPARATOR = "__"
    FLATTENING_PARALLELISM = "4"

    # Default pagination settings
    PAGINATION_ENABLED = "true"
    PAGINATION_MODE = "api"
    PAGINATION_SIZE = "100"

    # Default freshness settings
    FRESHNESS_ENABLED = "true"
    FRESHNESS_WARN_AFTER = "3600"
    FRESHNESS_ERROR_AFTER = "7200"

    # Default performance settings
    PERFORMANCE_OPTIMIZATION_ENABLED = "true"
    PERFORMANCE_MONITORING_ENABLED = "true"
    PERFORMANCE_METRICS_COLLECTION = "true"
    PERFORMANCE_ALERTING_ENABLED = "true"


# ==============================================================================
# DBT ORACLE WMS ENTITY TYPES - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleWMSEntityTypes(StrEnum):
    """DBT Oracle WMS entity types using flext-core types."""

    # Core Oracle WMS entities
    INVENTORY = "inventory"
    ORDERS = "orders"
    SHIPMENTS = "shipments"
    RECEIPTS = "receipts"
    LOCATIONS = "locations"
    ITEMS = "items"
    CUSTOMERS = "customers"
    SUPPLIERS = "suppliers"
    WAREHOUSES = "warehouses"
    FACILITIES = "facilities"

    # Transaction entities
    TRANSACTIONS = "transactions"
    ADJUSTMENTS = "adjustments"
    TRANSFERS = "transfers"
    ALLOCATIONS = "allocations"
    RESERVATIONS = "reservations"
    PICKS = "picks"
    PUTS = "puts"
    CYCLES = "cycles"
    COUNTS = "counts"
    MOVES = "moves"

    # Planning entities
    FORECASTS = "forecasts"
    PLANS = "plans"
    SCHEDULES = "schedules"
    REQUIREMENTS = "requirements"
    DEMANDS = "demands"
    SUPPLIES = "supplies"
    REPLENISHMENTS = "replenishments"
    OPTIMIZATIONS = "optimizations"
    SIMULATIONS = "simulations"
    SCENARIOS = "scenarios"

    # Operational entities
    TASKS = "tasks"
    JOBS = "jobs"
    WORKFLOWS = "workflows"
    PROCESSES = "processes"
    OPERATIONS = "operations"
    ACTIVITIES = "activities"
    EVENTS = "events"
    ALERTS = "alerts"
    NOTIFICATIONS = "notifications"
    EXCEPTIONS = "exceptions"

    # Configuration entities
    RULES = "rules"
    POLICIES = "policies"
    PARAMETERS = "parameters"
    SETTINGS = "settings"
    PREFERENCES = "preferences"
    CONFIGURATIONS = "configurations"
    PROFILES = "profiles"
    TEMPLATES = "templates"
    PATTERNS = "patterns"
    SCHEMAS = "schemas"

    # Analytical entities
    METRICS = "metrics"
    MEASURES = "measures"
    DIMENSIONS = "dimensions"
    FACTS = "facts"
    AGGREGATES = "aggregates"
    SUMMARIES = "summaries"
    REPORTS = "reports"
    DASHBOARDS = "dashboards"
    CHARTS = "charts"
    GRAPHS = "graphs"

    # Security entities
    USERS = "users"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    PRIVILEGES = "privileges"
    SESSIONS = "sessions"
    AUTHENTICATIONS = "authentications"
    AUTHORIZATIONS = "authorizations"
    ACCESS_LOGS = "access_logs"
    AUDIT_LOGS = "audit_logs"
    SECURITY_EVENTS = "security_events"

    # Integration entities
    INTERFACES = "interfaces"
    CONNECTIONS = "connections"
    ENDPOINTS = "endpoints"
    SERVICES = "services"
    APIS = "apis"
    PROTOCOLS = "protocols"
    FORMATS = "formats"
    TRANSFORMATIONS = "transformations"
    MAPPINGS = "mappings"
    SYNCHRONIZATIONS = "synchronizations"

    # Master data entities
    MASTER_DATA = "master_data"
    REFERENCE_DATA = "reference_data"
    LOOKUP_DATA = "lookup_data"
    HIERARCHIES = "hierarchies"
    CLASSIFICATIONS = "classifications"
    CATEGORIES = "categories"
    TYPES = "types"
    CODES = "codes"
    IDENTIFIERS = "identifiers"
    ATTRIBUTES = "attributes"

    # Historical entities
    HISTORY = "history"
    ARCHIVES = "archives"
    SNAPSHOTS = "snapshots"
    VERSIONS = "versions"
    REVISIONS = "revisions"
    CHANGES = "changes"
    DELTAS = "deltas"
    MODIFICATIONS = "modifications"
    UPDATES = "updates"
    EVOLUTION = "evolution"


# ==============================================================================
# DBT ORACLE WMS MATERIALIZATIONS - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleWMSMaterializations(StrEnum):
    """DBT Oracle WMS materialization types using flext-core types."""

    # Core DBT materializations
    TABLE = "table"
    VIEW = "view"
    INCREMENTAL = "incremental"
    EPHEMERAL = "ephemeral"
    SNAPSHOT = "snapshot"

    # Oracle WMS specific materializations
    MATERIALIZED_VIEW = "materialized_view"
    EXTERNAL_TABLE = "external_table"
    PARTITIONED_TABLE = "partitioned_table"
    COMPRESSED_TABLE = "compressed_table"
    INDEXED_TABLE = "indexed_table"

    # Analytical materializations
    FACT_TABLE = "fact_table"
    DIMENSION_TABLE = "dimension_table"
    AGGREGATE_TABLE = "aggregate_table"
    SUMMARY_TABLE = "summary_table"
    REPORT_TABLE = "report_table"

    # Operational materializations
    STAGING_TABLE = "staging_table"
    LANDING_TABLE = "landing_table"
    CLEANSING_TABLE = "cleansing_table"
    TRANSFORMATION_TABLE = "transformation_table"
    INTEGRATION_TABLE = "integration_table"

    # Temporary materializations
    TEMP_TABLE = "temp_table"
    WORK_TABLE = "work_table"
    SCRATCH_TABLE = "scratch_table"
    BUFFER_TABLE = "buffer_table"
    CACHE_TABLE = "cache_table"

    # Performance materializations
    CLUSTERED_TABLE = "clustered_table"
    HASH_TABLE = "hash_table"
    RANGE_TABLE = "range_table"
    LIST_TABLE = "list_table"
    COMPOSITE_TABLE = "composite_table"

    # Archive materializations
    ARCHIVE_TABLE = "archive_table"
    HISTORICAL_TABLE = "historical_table"
    BACKUP_TABLE = "backup_table"
    SNAPSHOT_TABLE = "snapshot_table"
    VERSION_TABLE = "version_table"

    # Specialized materializations
    LOOKUP_TABLE = "lookup_table"
    REFERENCE_TABLE = "reference_table"
    CONFIGURATION_TABLE = "configuration_table"
    PARAMETER_TABLE = "parameter_table"
    METADATA_TABLE = "metadata_table"


# ==============================================================================
# DBT ORACLE WMS TEST TYPES - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleWMSTestTypes(StrEnum):
    """DBT Oracle WMS test types using flext-core types."""

    # Core DBT tests
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    ACCEPTED_VALUES = "accepted_values"
    RELATIONSHIPS = "relationships"
    EXPRESSION = "expression"
    SCHEMA = "schema"
    DATA = "data"

    # Oracle WMS specific tests
    ORACLE_WMS_ENTITY_VALIDATION = "oracle_wms_entity_validation"
    ORACLE_WMS_SCHEMA_VALIDATION = "oracle_wms_schema_validation"
    ORACLE_WMS_CONNECTION_TEST = "oracle_wms_connection_test"
    ORACLE_WMS_API_TEST = "oracle_wms_api_test"
    ORACLE_WMS_AUTHENTICATION_TEST = "oracle_wms_authentication_test"

    # Data quality tests
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    TIMELINESS = "timeliness"
    UNIQUENESS = "uniqueness"
    INTEGRITY = "integrity"
    CONFORMITY = "conformity"
    RELEVANCE = "relevance"
    PRECISION = "precision"

    # Business rule tests
    BUSINESS_RULE = "business_rule"
    DOMAIN_RULE = "domain_rule"
    CONSTRAINT_RULE = "constraint_rule"
    VALIDATION_RULE = "validation_rule"
    TRANSFORMATION_RULE = "transformation_rule"
    CALCULATION_RULE = "calculation_rule"
    AGGREGATION_RULE = "aggregation_rule"
    ENRICHMENT_RULE = "enrichment_rule"
    CLEANSING_RULE = "cleansing_rule"
    STANDARDIZATION_RULE = "standardization_rule"

    # Performance tests
    PERFORMANCE = "performance"
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    SCALABILITY_TEST = "scalability_test"
    VOLUME_TEST = "volume_test"
    THROUGHPUT_TEST = "throughput_test"
    LATENCY_TEST = "latency_test"
    RESOURCE_TEST = "resource_test"
    CAPACITY_TEST = "capacity_test"
    EFFICIENCY_TEST = "efficiency_test"

    # Security tests
    SECURITY = "security"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ACCESS_CONTROL = "access_control"
    ENCRYPTION = "encryption"
    PRIVACY = "privacy"
    AUDIT = "audit"
    COMPLIANCE = "compliance"
    VULNERABILITY = "vulnerability"
    PENETRATION = "penetration"

    # Integration tests
    INTEGRATION = "integration"
    END_TO_END = "end_to_end"
    SYSTEM = "system"
    INTERFACE = "interface"
    API = "api"
    SERVICE = "service"
    WORKFLOW = "workflow"
    PROCESS = "process"
    PIPELINE = "pipeline"
    ORCHESTRATION = "orchestration"

    # Regression tests
    REGRESSION = "regression"
    BACKWARD_COMPATIBILITY = "backward_compatibility"
    FORWARD_COMPATIBILITY = "forward_compatibility"
    VERSION_COMPATIBILITY = "version_compatibility"
    PLATFORM_COMPATIBILITY = "platform_compatibility"
    ENVIRONMENT_COMPATIBILITY = "environment_compatibility"
    CONFIGURATION_COMPATIBILITY = "configuration_compatibility"
    DATA_COMPATIBILITY = "data_compatibility"
    SCHEMA_COMPATIBILITY = "schema_compatibility"
    API_COMPATIBILITY = "api_compatibility"

    # Monitoring tests
    MONITORING = "monitoring"
    ALERTING = "alerting"
    NOTIFICATION = "notification"
    LOGGING = "logging"
    TRACING = "tracing"
    METRICS = "metrics"
    HEALTH_CHECK = "health_check"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"
    RECOVERY = "recovery"


# ==============================================================================
# DBT ORACLE WMS MACRO TYPES - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleWMSMacroTypes(StrEnum):
    """DBT Oracle WMS macro types using flext-core types."""

    # Core DBT macros
    FUNCTION = "function"
    OPERATION = "operation"
    TEST = "test"
    MATERIALIZATION = "materialization"
    HOOK = "hook"
    ADAPTER = "adapter"

    # Oracle WMS specific macros
    ORACLE_WMS_ENTITY_MACRO = "oracle_wms_entity_macro"
    ORACLE_WMS_SCHEMA_MACRO = "oracle_wms_schema_macro"
    ORACLE_WMS_CONNECTION_MACRO = "oracle_wms_connection_macro"
    ORACLE_WMS_API_MACRO = "oracle_wms_api_macro"
    ORACLE_WMS_AUTHENTICATION_MACRO = "oracle_wms_authentication_macro"
    ORACLE_WMS_AUTHORIZATION_MACRO = "oracle_wms_authorization_macro"
    ORACLE_WMS_FILTER_MACRO = "oracle_wms_filter_macro"
    ORACLE_WMS_SORT_MACRO = "oracle_wms_sort_macro"
    ORACLE_WMS_PAGINATION_MACRO = "oracle_wms_pagination_macro"
    ORACLE_WMS_FLATTENING_MACRO = "oracle_wms_flattening_macro"

    # Data transformation macros
    TRANSFORMATION = "transformation"
    CLEANSING = "cleansing"
    VALIDATION = "validation"
    STANDARDIZATION = "standardization"
    ENRICHMENT = "enrichment"
    AGGREGATION = "aggregation"
    CALCULATION = "calculation"
    CONVERSION = "conversion"
    FORMATTING = "formatting"
    PARSING = "parsing"

    # Utility macros
    UTILITY = "utility"
    HELPER = "helper"
    COMMON = "common"
    GENERIC = "generic"
    REUSABLE = "reusable"
    SHARED = "shared"
    LIBRARY = "library"
    TOOLKIT = "toolkit"
    FRAMEWORK = "framework"
    TEMPLATE = "template"

    # Generation macros
    GENERATION = "generation"
    BUILDER = "builder"
    FACTORY = "factory"
    CREATOR = "creator"
    CONSTRUCTOR = "constructor"
    ASSEMBLER = "assembler"
    COMPILER = "compiler"
    RENDERER = "renderer"
    FORMATTER = "formatter"
    SERIALIZER = "serializer"

    # Analysis macros
    ANALYSIS = "analysis"
    ANALYTICAL = "analytical"
    STATISTICAL = "statistical"
    MATHEMATICAL = "mathematical"
    ALGORITHMIC = "algorithmic"
    COMPUTATIONAL = "computational"
    PROCEDURAL = "procedural"
    FUNCTIONAL = "functional"
    LOGICAL = "logical"
    CONDITIONAL = "conditional"

    # Integration macros
    INTEGRATION = "integration"
    INTERFACE = "interface"
    CONNECTOR = "connector"
    BRIDGE = "bridge"
    GATEWAY = "gateway"
    PROXY = "proxy"
    WRAPPER = "wrapper"
    FACADE = "facade"
    DECORATOR = "decorator"

    # Performance macros
    PERFORMANCE = "performance"
    OPTIMIZATION = "optimization"
    EFFICIENCY = "efficiency"
    ACCELERATION = "acceleration"
    CACHING = "caching"
    INDEXING = "indexing"
    PARTITIONING = "partitioning"
    CLUSTERING = "clustering"
    COMPRESSION = "compression"
    PARALLELIZATION = "parallelization"

    # Security macros
    SECURITY = "security"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    HASHING = "hashing"
    SIGNING = "signing"
    VERIFICATION = "verification"
    SANITIZATION = "sanitization"

    # Monitoring macros
    MONITORING = "monitoring"
    LOGGING = "logging"
    TRACING = "tracing"
    METRICS = "metrics"
    ALERTING = "alerting"
    NOTIFICATION = "notification"
    REPORTING = "reporting"
    DASHBOARD = "dashboard"
    VISUALIZATION = "visualization"
    ANALYTICS = "analytics"

    # Maintenance macros
    MAINTENANCE = "maintenance"
    HOUSEKEEPING = "housekeeping"
    CLEANUP = "cleanup"
    ARCHIVING = "archiving"
    BACKUP = "backup"
    RESTORE = "restore"
    MIGRATION = "migration"
    UPGRADE = "upgrade"
    PATCHING = "patching"
    RECOVERY = "recovery"


# ==============================================================================
# DBT ORACLE WMS DOCUMENTATION TYPES - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleWMSDocumentationTypes(StrEnum):
    """DBT Oracle WMS documentation types using flext-core types."""

    # Core documentation types
    MODEL = "model"
    SOURCE = "source"
    TEST = "test"
    MACRO = "macro"
    SNAPSHOT = "snapshot"
    ANALYSIS = "analysis"

    # Oracle WMS specific documentation
    ORACLE_WMS_ENTITY = "oracle_wms_entity"
    ORACLE_WMS_SCHEMA = "oracle_wms_schema"
    ORACLE_WMS_CONNECTION = "oracle_wms_connection"
    ORACLE_WMS_API = "oracle_wms_api"
    ORACLE_WMS_AUTHENTICATION = "oracle_wms_authentication"
    ORACLE_WMS_AUTHORIZATION = "oracle_wms_authorization"
    ORACLE_WMS_FILTER = "oracle_wms_filter"
    ORACLE_WMS_SORT = "oracle_wms_sort"
    ORACLE_WMS_PAGINATION = "oracle_wms_pagination"
    ORACLE_WMS_FLATTENING = "oracle_wms_flattening"

    # Technical documentation
    TECHNICAL = "technical"
    ARCHITECTURAL = "architectural"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    SPECIFICATION = "specification"
    REQUIREMENTS = "requirements"
    STANDARDS = "standards"
    GUIDELINES = "guidelines"
    BEST_PRACTICES = "best_practices"
    PATTERNS = "patterns"

    # User documentation
    USER = "user"
    FUNCTIONAL = "functional"
    OPERATIONAL = "operational"
    PROCEDURAL = "procedural"
    INSTRUCTIONAL = "instructional"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    MANUAL = "manual"
    HANDBOOK = "handbook"
    REFERENCE = "reference"

    # Process documentation
    PROCESS = "process"
    WORKFLOW = "workflow"
    PROCEDURE = "procedure"
    PROTOCOL = "protocol"
    METHODOLOGY = "methodology"
    FRAMEWORK = "framework"
    APPROACH = "approach"
    STRATEGY = "strategy"
    PLAN = "plan"
    ROADMAP = "roadmap"

    # Quality documentation
    QUALITY = "quality"
    VALIDATION = "validation"
    VERIFICATION = "verification"
    TESTING = "testing"
    REVIEW = "review"
    AUDIT = "audit"
    ASSESSMENT = "assessment"
    EVALUATION = "evaluation"
    INSPECTION = "inspection"
    CERTIFICATION = "certification"

    # Configuration documentation
    CONFIGURATION = "configuration"
    SETUP = "setup"
    INSTALLATION = "installation"
    DEPLOYMENT = "deployment"
    ENVIRONMENT = "environment"
    PARAMETER = "parameter"
    SETTING = "setting"
    PREFERENCE = "preference"
    OPTION = "option"
    PROPERTY = "property"

    # Integration documentation
    INTEGRATION = "integration"
    INTERFACE = "interface"
    CONNECTOR = "connector"
    ADAPTER = "adapter"
    BRIDGE = "bridge"
    GATEWAY = "gateway"
    PROXY = "proxy"
    WRAPPER = "wrapper"
    FACADE = "facade"
    DECORATOR = "decorator"

    # Performance documentation
    PERFORMANCE = "performance"
    OPTIMIZATION = "optimization"
    EFFICIENCY = "efficiency"
    SCALABILITY = "scalability"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE = "resource"
    CAPACITY = "capacity"
    UTILIZATION = "utilization"
    BOTTLENECK = "bottleneck"

    # Security documentation
    SECURITY = "security"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    PRIVACY = "privacy"
    COMPLIANCE = "compliance"
    VULNERABILITY = "vulnerability"
    THREAT = "threat"
    RISK = "risk"
    MITIGATION = "mitigation"

    # Monitoring documentation
    MONITORING = "monitoring"
    LOGGING = "logging"
    TRACING = "tracing"
    METRICS = "metrics"
    ALERTING = "alerting"
    NOTIFICATION = "notification"
    REPORTING = "reporting"
    DASHBOARD = "dashboard"
    VISUALIZATION = "visualization"
    ANALYTICS = "analytics"

    # Maintenance documentation
    MAINTENANCE = "maintenance"
    SUPPORT = "support"
    TROUBLESHOOTING = "troubleshooting"
    DEBUGGING = "debugging"
    DIAGNOSIS = "diagnosis"
    RESOLUTION = "resolution"
    WORKAROUND = "workaround"
    FAQ = "faq"
    KNOWLEDGE_BASE = "knowledge_base"
    HELP = "help"


# ==============================================================================
# FINAL CONSTANTS AGGREGATION
# ==============================================================================


# Timeout constants
DEFAULT_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_CONNECTION_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_QUERY_TIMEOUT_SECONDS: Final[int] = 300
DEFAULT_COMPILATION_TIMEOUT_SECONDS: Final[int] = 600
DEFAULT_EXECUTION_TIMEOUT_SECONDS: Final[int] = 3600
DEFAULT_TEST_TIMEOUT_SECONDS: Final[int] = 300
DEFAULT_DOCUMENTATION_TIMEOUT_SECONDS: Final[int] = 300

# Retry constants
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_CONNECTION_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_QUERY_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_COMPILATION_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_EXECUTION_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_TEST_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_DOCUMENTATION_RETRY_ATTEMPTS: Final[int] = 3

# Parallelism constants
DEFAULT_PARALLELISM: Final[int] = 4
DEFAULT_CONNECTION_PARALLELISM: Final[int] = 4
DEFAULT_QUERY_PARALLELISM: Final[int] = 4
DEFAULT_COMPILATION_PARALLELISM: Final[int] = 4
DEFAULT_EXECUTION_PARALLELISM: Final[int] = 4
DEFAULT_TEST_PARALLELISM: Final[int] = 4
DEFAULT_DOCUMENTATION_PARALLELISM: Final[int] = 4

# Resource constants
DEFAULT_MEMORY_MB: Final[int] = 1024
DEFAULT_CPU_PERCENT: Final[int] = 80
DEFAULT_DISK_MB: Final[int] = 10240

# Batch constants
DEFAULT_BATCH_SIZE: Final[int] = 1000
DEFAULT_CONNECTION_BATCH_SIZE: Final[int] = 100
DEFAULT_QUERY_BATCH_SIZE: Final[int] = 1000
DEFAULT_COMPILATION_BATCH_SIZE: Final[int] = 100
DEFAULT_EXECUTION_BATCH_SIZE: Final[int] = 100
DEFAULT_TEST_BATCH_SIZE: Final[int] = 100
DEFAULT_DOCUMENTATION_BATCH_SIZE: Final[int] = 100

# Cache constants
DEFAULT_CACHE_TTL_SECONDS: Final[int] = 3600
DEFAULT_CACHE_MAX_SIZE: Final[int] = 1000
DEFAULT_CACHE_ENABLED: Final[bool] = True
DEFAULT_CACHE_COMPRESSION: Final[bool] = True

# Retention constants
DEFAULT_RETENTION_DAYS: Final[int] = 30
DEFAULT_LOG_RETENTION_DAYS: Final[int] = 30
DEFAULT_METRICS_RETENTION_DAYS: Final[int] = 90
DEFAULT_DOCUMENTATION_RETENTION_DAYS: Final[int] = 365
DEFAULT_BACKUP_RETENTION_DAYS: Final[int] = 90

# Oracle WMS constants
DEFAULT_ORACLE_WMS_PAGE_SIZE: Final[int] = 100
DEFAULT_ORACLE_WMS_PAGE_MODE: Final[str] = "api"
DEFAULT_ORACLE_WMS_FLATTENING_DEPTH: Final[int] = 10
DEFAULT_ORACLE_WMS_FLATTENING_SEPARATOR: Final[str] = "__"
DEFAULT_ORACLE_WMS_ENTITY_REFRESH_INTERVAL: Final[int] = 3600
DEFAULT_ORACLE_WMS_SCHEMA_REFRESH_INTERVAL: Final[int] = 3600
DEFAULT_ORACLE_WMS_ENTITY_CACHE_TTL: Final[int] = 1800
DEFAULT_ORACLE_WMS_SCHEMA_CACHE_TTL: Final[int] = 1800

# Freshness constants
DEFAULT_FRESHNESS_WARN_AFTER_SECONDS: Final[int] = 3600
DEFAULT_FRESHNESS_ERROR_AFTER_SECONDS: Final[int] = 7200

# Limits constants
DEFAULT_MAX_MODELS: Final[int] = 1000
DEFAULT_MAX_SOURCES: Final[int] = 1000
DEFAULT_MAX_TESTS: Final[int] = 10000
DEFAULT_MAX_MACROS: Final[int] = 1000
DEFAULT_MAX_SNAPSHOTS: Final[int] = 100
DEFAULT_MAX_ANALYSES: Final[int] = 100

# Boolean constants
DEFAULT_ENABLED: Final[bool] = True
DEFAULT_DEBUG: Final[bool] = False
DEFAULT_MONITORING_ENABLED: Final[bool] = True
DEFAULT_METRICS_ENABLED: Final[bool] = True
DEFAULT_HEALTH_CHECKS_ENABLED: Final[bool] = True
DEFAULT_SECURITY_ENABLED: Final[bool] = True
DEFAULT_ENCRYPTION_ENABLED: Final[bool] = True
DEFAULT_SSL_ENABLED: Final[bool] = True
DEFAULT_SSL_VERIFY: Final[bool] = True
DEFAULT_BACKUP_ENABLED: Final[bool] = True
DEFAULT_BACKUP_COMPRESSION: Final[bool] = True
DEFAULT_ENTITY_DISCOVERY_ENABLED: Final[bool] = True
DEFAULT_ENTITY_VALIDATION_ENABLED: Final[bool] = True
DEFAULT_SCHEMA_DISCOVERY_ENABLED: Final[bool] = True
DEFAULT_SCHEMA_VALIDATION_ENABLED: Final[bool] = True
DEFAULT_FILTER_ENABLED: Final[bool] = True
DEFAULT_FILTER_CACHE_ENABLED: Final[bool] = True
DEFAULT_FLATTENING_ENABLED: Final[bool] = True
DEFAULT_PAGINATION_ENABLED: Final[bool] = True
DEFAULT_FRESHNESS_ENABLED: Final[bool] = True
DEFAULT_PERFORMANCE_OPTIMIZATION_ENABLED: Final[bool] = True
DEFAULT_PERFORMANCE_MONITORING_ENABLED: Final[bool] = True
DEFAULT_PERFORMANCE_METRICS_COLLECTION: Final[bool] = True
DEFAULT_PERFORMANCE_ALERTING_ENABLED: Final[bool] = True
DEFAULT_VALIDATION_ENABLED: Final[bool] = True
DEFAULT_DOCUMENTATION_ENABLED: Final[bool] = True
DEFAULT_DOCUMENTATION_AUTO_GENERATE: Final[bool] = True

# String constants
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_ORACLE_WMS_API_VERSION: Final[str] = "v1"
DEFAULT_ORACLE_WMS_AUTH_METHOD: Final[str] = "basic"
DEFAULT_ORACLE_WMS_COMPANY_CODE: Final[str] = "DEFAULT"
DEFAULT_ORACLE_WMS_FACILITY_CODE: Final[str] = "MAIN"
DEFAULT_ORACLE_WMS_BASE_URL: Final[str] = "https://oracle-wms.example.com/api"
DEFAULT_DBT_VERSION: Final[str] = "1.8.0"
DEFAULT_DBT_TARGET: Final[str] = "default"
DEFAULT_DBT_PROFILE: Final[str] = "oracle_wms"
DEFAULT_MATERIALIZATION: Final[str] = "table"
DEFAULT_MATERIALIZATION_STRATEGY: Final[str] = "full_refresh"
DEFAULT_TEST_SEVERITY: Final[str] = "error"
DEFAULT_DOCUMENTATION_FORMAT: Final[str] = "markdown"
DEFAULT_PROJECT_NAME: Final[str] = "dbt_oracle_wms_project"
DEFAULT_PROJECT_VERSION: Final[str] = "1.0.0"
DEFAULT_PROJECT_DESCRIPTION: Final[str] = "DBT Oracle WMS data transformation project"

# ==============================================================================
# EXPORT PUBLIC API
# ==============================================================================

__all__ = [
    "DEFAULT_BACKUP_COMPRESSION",
    "DEFAULT_BACKUP_ENABLED",
    "DEFAULT_BACKUP_RETENTION_DAYS",
    # Batch constants
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_CACHE_COMPRESSION",
    "DEFAULT_CACHE_ENABLED",
    "DEFAULT_CACHE_MAX_SIZE",
    # Cache constants
    "DEFAULT_CACHE_TTL_SECONDS",
    "DEFAULT_COMPILATION_BATCH_SIZE",
    "DEFAULT_COMPILATION_PARALLELISM",
    "DEFAULT_COMPILATION_RETRY_ATTEMPTS",
    "DEFAULT_COMPILATION_TIMEOUT_SECONDS",
    "DEFAULT_CONNECTION_BATCH_SIZE",
    "DEFAULT_CONNECTION_PARALLELISM",
    "DEFAULT_CONNECTION_RETRY_ATTEMPTS",
    "DEFAULT_CONNECTION_TIMEOUT_SECONDS",
    "DEFAULT_CPU_PERCENT",
    "DEFAULT_DBT_PROFILE",
    "DEFAULT_DBT_TARGET",
    "DEFAULT_DBT_VERSION",
    "DEFAULT_DEBUG",
    "DEFAULT_DISK_MB",
    "DEFAULT_DOCUMENTATION_AUTO_GENERATE",
    "DEFAULT_DOCUMENTATION_BATCH_SIZE",
    "DEFAULT_DOCUMENTATION_ENABLED",
    "DEFAULT_DOCUMENTATION_FORMAT",
    "DEFAULT_DOCUMENTATION_PARALLELISM",
    "DEFAULT_DOCUMENTATION_RETENTION_DAYS",
    "DEFAULT_DOCUMENTATION_RETRY_ATTEMPTS",
    "DEFAULT_DOCUMENTATION_TIMEOUT_SECONDS",
    # Boolean constants
    "DEFAULT_ENABLED",
    "DEFAULT_ENCRYPTION_ENABLED",
    "DEFAULT_ENTITY_DISCOVERY_ENABLED",
    "DEFAULT_ENTITY_VALIDATION_ENABLED",
    "DEFAULT_EXECUTION_BATCH_SIZE",
    "DEFAULT_EXECUTION_PARALLELISM",
    "DEFAULT_EXECUTION_RETRY_ATTEMPTS",
    "DEFAULT_EXECUTION_TIMEOUT_SECONDS",
    "DEFAULT_FILTER_CACHE_ENABLED",
    "DEFAULT_FILTER_ENABLED",
    "DEFAULT_FLATTENING_ENABLED",
    "DEFAULT_FRESHNESS_ENABLED",
    "DEFAULT_FRESHNESS_ERROR_AFTER_SECONDS",
    # Freshness constants
    "DEFAULT_FRESHNESS_WARN_AFTER_SECONDS",
    "DEFAULT_HEALTH_CHECKS_ENABLED",
    # String constants
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_RETENTION_DAYS",
    "DEFAULT_MATERIALIZATION",
    "DEFAULT_MATERIALIZATION_STRATEGY",
    "DEFAULT_MAX_ANALYSES",
    "DEFAULT_MAX_MACROS",
    # Limits constants
    "DEFAULT_MAX_MODELS",
    "DEFAULT_MAX_SNAPSHOTS",
    "DEFAULT_MAX_SOURCES",
    "DEFAULT_MAX_TESTS",
    # Resource constants
    "DEFAULT_MEMORY_MB",
    "DEFAULT_METRICS_ENABLED",
    "DEFAULT_METRICS_RETENTION_DAYS",
    "DEFAULT_MONITORING_ENABLED",
    "DEFAULT_ORACLE_WMS_API_VERSION",
    "DEFAULT_ORACLE_WMS_AUTH_METHOD",
    "DEFAULT_ORACLE_WMS_BASE_URL",
    "DEFAULT_ORACLE_WMS_COMPANY_CODE",
    "DEFAULT_ORACLE_WMS_ENTITY_CACHE_TTL",
    "DEFAULT_ORACLE_WMS_ENTITY_REFRESH_INTERVAL",
    "DEFAULT_ORACLE_WMS_FACILITY_CODE",
    "DEFAULT_ORACLE_WMS_FLATTENING_DEPTH",
    "DEFAULT_ORACLE_WMS_FLATTENING_SEPARATOR",
    "DEFAULT_ORACLE_WMS_PAGE_MODE",
    # Oracle WMS constants
    "DEFAULT_ORACLE_WMS_PAGE_SIZE",
    "DEFAULT_ORACLE_WMS_SCHEMA_CACHE_TTL",
    "DEFAULT_ORACLE_WMS_SCHEMA_REFRESH_INTERVAL",
    "DEFAULT_PAGINATION_ENABLED",
    # Parallelism constants
    "DEFAULT_PARALLELISM",
    "DEFAULT_PERFORMANCE_ALERTING_ENABLED",
    "DEFAULT_PERFORMANCE_METRICS_COLLECTION",
    "DEFAULT_PERFORMANCE_MONITORING_ENABLED",
    "DEFAULT_PERFORMANCE_OPTIMIZATION_ENABLED",
    "DEFAULT_PROJECT_DESCRIPTION",
    "DEFAULT_PROJECT_NAME",
    "DEFAULT_PROJECT_VERSION",
    "DEFAULT_QUERY_BATCH_SIZE",
    "DEFAULT_QUERY_PARALLELISM",
    "DEFAULT_QUERY_RETRY_ATTEMPTS",
    "DEFAULT_QUERY_TIMEOUT_SECONDS",
    # Retention constants
    "DEFAULT_RETENTION_DAYS",
    # Retry constants
    "DEFAULT_RETRY_ATTEMPTS",
    "DEFAULT_SCHEMA_DISCOVERY_ENABLED",
    "DEFAULT_SCHEMA_VALIDATION_ENABLED",
    "DEFAULT_SECURITY_ENABLED",
    "DEFAULT_SSL_ENABLED",
    "DEFAULT_SSL_VERIFY",
    "DEFAULT_TEST_BATCH_SIZE",
    "DEFAULT_TEST_PARALLELISM",
    "DEFAULT_TEST_RETRY_ATTEMPTS",
    "DEFAULT_TEST_SEVERITY",
    "DEFAULT_TEST_TIMEOUT_SECONDS",
    # Timeout constants
    "DEFAULT_TIMEOUT_SECONDS",
    "DEFAULT_VALIDATION_ENABLED",
    # Enum classes
    "DBTOracleWMSDefaults",
    "DBTOracleWMSDocumentationTypes",
    "DBTOracleWMSEntityTypes",
    "DBTOracleWMSMacroTypes",
    "DBTOracleWMSMaterializations",
    "DBTOracleWMSTestTypes",
]
