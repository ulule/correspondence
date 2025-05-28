import * as React from "react";

import { Error } from "../types";

type FuncValidator<PROPS> = (
  props: PROPS & { errors?: Error[] }
) => React.ReactNode;

export default function withFormikValidator<
  PROPS,
  FORM_ERRORS extends Record<string, any>,
>(
  Component: React.JSXElementConstructor<PROPS & { formErrors: FORM_ERRORS }>
): FuncValidator<PROPS> {
  const Validator = (
    props: PROPS & { errors?: Error[] }
  ): React.ReactElement => {
    const formatErrors = (errors: Error[]): FORM_ERRORS => {
      const results = errors.reduce((accumulator, field) => {
        return {
          ...accumulator,
          [field.loc[field.loc.length - 1]]: field.msg,
        };
      }, {} as FORM_ERRORS);

      return results;
    };

    const results = formatErrors(props.errors || []);

    return <Component {...props} formErrors={results} />;
  };

  return Validator;
}
