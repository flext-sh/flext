-- Oracle WMS utility macros for enterprise data transformations

-- Macro to create audit log entries for Oracle WMS operations
{% macro create_audit_log_entry(operation_type) %}
  {% if target.schema %}
    insert into {{ target.schema }}.wms_audit_log (
      operation_type,
      dbt_run_id,
      operation_timestamp,
      target_environment,
      model_count,
      execution_user
    ) values (
      '{{ operation_type }}',
      '{{ invocation_id }}',
      current_timestamp,
      '{{ target.name }}',
      {{ graph.nodes.values() | selectattr("resource_type", "equalto", "model") | list | length }},
      '{{ env_var("DBT_USER", "system") }}'
    )
  {% endif %}
{% endmacro %}

-- Macro to update data quality metrics for Oracle WMS models
{% macro update_data_quality_metrics() %}
  {% if target.schema %}
    -- Update data quality metrics table with latest run statistics
    merge into {{ target.schema }}.wms_data_quality_metrics target
    using (
      select 
        '{{ invocation_id }}' as run_id,
        current_timestamp as run_timestamp,
        '{{ target.name }}' as environment,
        'dbt_run' as metric_type,
        '{{ graph.nodes.values() | selectattr("resource_type", "equalto", "model") | list | length }}' as model_count,
        case 
          when {{ var('enable_audit_logging', true) }} then 'enabled'
          else 'disabled'
        end as audit_status
    ) source
    on (target.run_id = source.run_id)
    when not matched then
      insert (run_id, run_timestamp, environment, metric_type, model_count, audit_status)
      values (source.run_id, source.run_timestamp, source.environment, source.metric_type, source.model_count, source.audit_status)
  {% endif %}
{% endmacro %}

-- Macro to standardize Oracle WMS company and facility codes
{% macro standardize_wms_codes(company_field, facility_field) %}
  upper(trim({{ company_field }})) as {{ company_field }},
  upper(trim({{ facility_field }})) as {{ facility_field }}
{% endmacro %}

-- Macro to convert Oracle WMS timestamps to standard format
{% macro standardize_wms_timestamp(timestamp_field) %}
  case 
    when {{ timestamp_field }} is not null then 
      cast({{ timestamp_field }} as timestamp)
    else null 
  end
{% endmacro %}

-- Macro to generate Oracle WMS business keys
{% macro generate_wms_business_key(entity_type, key_fields) %}
  {% set key_concat = key_fields | join("|| '_' ||") %}
  '{{ entity_type }}_' || {{ key_concat }} as business_key
{% endmacro %}

-- Macro to handle Oracle WMS quantity fields with proper numeric conversion
{% macro standardize_wms_quantity(quantity_field, default_value=0) %}
  case 
    when {{ quantity_field }} is not null and {{ quantity_field }} != '' then 
      cast({{ quantity_field }} as number(15,4))
    else {{ default_value }}
  end
{% endmacro %}

-- Macro to create Oracle WMS data quality checks
{% macro wms_data_quality_check(table_name, quality_rules) %}
  {% for rule in quality_rules %}
    select 
      '{{ table_name }}' as table_name,
      '{{ rule.name }}' as rule_name,
      '{{ rule.description }}' as rule_description,
      count(*) as violation_count,
      current_timestamp as check_timestamp
    from {{ table_name }}
    where not ({{ rule.condition }})
    
    {% if not loop.last %}
    union all
    {% endif %}
  {% endfor %}
{% endmacro %}

-- Macro to handle Oracle WMS status code mapping
{% macro map_wms_status(status_field, entity_type) %}
  case {{ status_field }}
    {% if entity_type == 'allocation' %}
      when 10 then 'PLANNED'
      when 20 then 'RELEASED' 
      when 30 then 'PICKING'
      when 40 then 'PICKED'
      when 50 then 'PACKED'
      when 90 then 'CANCELLED'
    {% elif entity_type == 'order' %}
      when 10 then 'CREATED'
      when 20 then 'RELEASED'
      when 30 then 'IN_PROGRESS'
      when 40 then 'COMPLETED'
      when 90 then 'CANCELLED'
    {% elif entity_type == 'inventory' %}
      when 10 then 'AVAILABLE'
      when 20 then 'ALLOCATED'
      when 30 then 'PICKED'
      when 40 then 'SHIPPED'
      when 50 then 'RESERVED'
    {% endif %}
    else 'UNKNOWN'
  end
{% endmacro %}

-- Macro to generate Oracle WMS incremental strategy
{% macro wms_incremental_strategy(timestamp_field='mod_ts') %}
  {% if is_incremental() %}
    where {{ timestamp_field }} > (select max({{ timestamp_field }}) from {{ this }})
  {% endif %}
{% endmacro %}

-- Macro to create Oracle WMS fact table with proper partitioning
{% macro create_wms_fact_table(table_name, partition_field='business_date') %}
  {{ config(
    materialized='incremental',
    unique_key=['company_code', 'facility_code', partition_field, 'entity_id'],
    on_schema_change='append_new_columns',
    incremental_strategy='merge'
  ) }}
{% endmacro %}

-- Macro to calculate Oracle WMS KPIs with proper error handling
{% macro calculate_wms_kpi(numerator, denominator, kpi_name) %}
  case 
    when {{ denominator }} > 0 then 
      round(({{ numerator }} / {{ denominator }}) * 100, 2)
    else 0 
  end as {{ kpi_name }}
{% endmacro %}

-- Macro to handle Oracle WMS boolean flags
{% macro standardize_wms_boolean(boolean_field) %}
  case 
    when upper({{ boolean_field }}) = 'Y' then true
    when upper({{ boolean_field }}) = 'N' then false
    else null
  end
{% endmacro %}

-- Macro to create Oracle WMS dimension with SCD Type 2
{% macro create_wms_dimension(natural_key_fields, effective_date_field='created_timestamp') %}
  {% set natural_key = natural_key_fields | join(', ') %}
  select 
    {{ dbt_utils.generate_surrogate_key(natural_key_fields) }} as dimension_key,
    {{ natural_key }},
    {{ effective_date_field }} as effective_from_date,
    lead({{ effective_date_field }}, 1) over (
      partition by {{ natural_key }} 
      order by {{ effective_date_field }}
    ) as effective_to_date,
    case 
      when lead({{ effective_date_field }}, 1) over (
        partition by {{ natural_key }} 
        order by {{ effective_date_field }}
      ) is null then true 
      else false 
    end as is_current,
    current_timestamp as dbt_created_at
{% endmacro %}

-- Macro for Oracle WMS entity validation
{% macro validate_wms_entity(entity_name, required_fields) %}
  {% for field in required_fields %}
    {% set test_name = entity_name ~ '_' ~ field ~ '_not_null' %}
    {{ config(
      pre_hook="insert into wms_validation_log 
        select '{{ test_name }}', count(*), current_timestamp 
        from {{ this }} 
        where {{ field }} is null"
    ) }}
  {% endfor %}
{% endmacro %}