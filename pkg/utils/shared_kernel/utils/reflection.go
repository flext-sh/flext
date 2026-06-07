package utils

import (
	"fmt"
	"reflect"
)

// GetFieldValue gets field value from struct using reflection
func GetFieldValue(obj any, fieldName string) (any, error) {
	val := reflect.ValueOf(obj)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	if val.Kind() != reflect.Struct {
		return nil, fmt.Errorf("object is not a struct")
	}

	field := val.FieldByName(fieldName)
	if !field.IsValid() {
		return nil, fmt.Errorf("field %s not found", fieldName)
	}

	return field.Interface(), nil
}

// SetFieldValue sets field value on struct using reflection
func SetFieldValue(obj any, fieldName string, value any) error {
	val := reflect.ValueOf(obj)
	var err error

	if val.Kind() != reflect.Ptr {
		err = fmt.Errorf("object must be a pointer")
	} else {
		val = val.Elem()
		if val.Kind() != reflect.Struct {
			err = fmt.Errorf("object is not a struct")
		} else {
			field := val.FieldByName(fieldName)
			fieldValue := reflect.ValueOf(value)
			switch {
			case !field.IsValid():
				err = fmt.Errorf("field %s not found", fieldName)
			case !field.CanSet():
				err = fmt.Errorf("field %s cannot be set", fieldName)
			case !fieldValue.Type().AssignableTo(field.Type()):
				err = fmt.Errorf("value type %s not assignable to field type %s",
					fieldValue.Type(), field.Type())
			default:
				field.Set(fieldValue)
			}
		}
	}

	return err
}

// GetStructFields returns all field names of a struct
func GetStructFields(obj any) []string {
	val := reflect.ValueOf(obj)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	if val.Kind() != reflect.Struct {
		return nil
	}

	typ := val.Type()
	fields := make([]string, typ.NumField())
	for i := 0; i < typ.NumField(); i++ {
		fields[i] = typ.Field(i).Name
	}
	return fields
}
