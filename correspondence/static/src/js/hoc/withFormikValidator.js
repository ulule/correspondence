import React from "react";

const withFormikValidator = Component => {
  const Validator = props => {
    const formatErrors = errors => {
      const results = errors.reduce((accumulator, field) => {
        return {
          ...accumulator,
          [field.loc[field.loc.length - 1]]: field.msg
        };
      }, {});

      return results;
    };

    const results = formatErrors(props.errors || []);

    return <Component {...props} formErrors={results} />;
  };

  return Validator;
};

export default withFormikValidator;
