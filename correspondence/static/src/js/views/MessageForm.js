import React, { useEffect, useRef } from "react";
import { Formik } from "formik";
import classNames from "classnames";
import * as Yup from "yup";

const MessageSchema = Yup.object().shape({
  body: Yup.string().required("This field is required."),
});

const DEFAULT_MAX_LENGTH = 160;

const MessageForm = ({
  onSubmit,
  focus,
  maxLength = DEFAULT_MAX_LENGTH,
} = props) => {
  let formSubmit;
  let formReset;

  const bodyFieldRef = useRef(null);

  const handleKeydown = (e) => {
    // Handle cmd+enter & ctrl+enter
    if (e.keyCode === 13 && (e.metaKey || e.ctrlKey) && formSubmit) {
      formSubmit();
    }
  };
  useEffect(() => {
    if (focus) {
      bodyFieldRef.current.focus();
    }

    document.addEventListener("keydown", handleKeydown);

    return () => {
      document.removeEventListener("keydown", handleKeydown);
    };
  });

  return (
    <Formik
      initialValues={{ body: "" }}
      validationSchema={MessageSchema}
      validateOnBlur={false}
      validateOnChange={false}
      onSubmit={(values, { setSubmitting }) => {
        onSubmit(values, () => {
          setSubmitting(false);
          formReset({ body: "" });
        });
      }}
    >
      {({
        values,
        errors,
        touched,
        handleChange,
        handleBlur,
        handleSubmit,
        isSubmitting,
        resetForm,
      }) => {
        formSubmit = handleSubmit;
        formReset = resetForm;
        return (
          <form onSubmit={handleSubmit}>
            <div className="conversation__message__form">
              <div className="field message__field">
                <div
                  className={classNames({
                    control: true,
                    "is-loading": isSubmitting,
                  })}
                >
                  <textarea
                    name="body"
                    className={classNames({
                      textarea: true,
                      "is-danger": errors.body,
                    })}
                    placeholder="Message..."
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values && values.body}
                  ></textarea>
                  {errors.body && (
                    <p className="help is-danger">{errors.body}</p>
                  )}
                </div>
              </div>

              <div className="field is-grouped is-grouped-right">
                <div className="control control__countdown">
                  <div
                    className={classNames("countdown", {
                      "countdown--danger":
                        values && values.body && values.body.length > maxLength,
                    })}
                  >
                    {(values && values.body && values.body.length) || 0}/
                    {maxLength}
                  </div>
                </div>
                <div
                  className={classNames({
                    control: true,
                    "is-loading": isSubmitting,
                  })}
                >
                  <button
                    className="button is-link"
                    type="submit"
                    disabled={isSubmitting}
                  >
                    Submit
                  </button>
                </div>
              </div>
            </div>
          </form>
        );
      }}
    </Formik>
  );
};

export default MessageForm;
