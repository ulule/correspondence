import * as React from "react";
import * as Yup from "yup";
import { Formik, FormikState } from "formik";
import withFormikValidator from "../hoc/withFormikValidator";
import * as types from "../types";

function filterNulls(obj: types.P): types.FormData {
  const newObj = { ...obj };

  Object.keys(newObj).forEach((key) => {
    if (newObj[key] === null) {
      newObj[key] = "";
    }
  });

  return newObj;
}

const UserSchema = Yup.object().shape({
  email: Yup.string().nullable().email("Invalid format"),
  manager_id: Yup.number().integer().required("This field is required"),
  country: Yup.string().required("This field is required"),
  phone_number: Yup.string().required("This field is required."),
});

type UserFormProps = {
  user?: types.User;
  onSubmit?: (ev: types.OnUserUpdateEvent) => void;
  submit?: boolean;
  onErrors?: (values: types.P) => void;
  formErrors?: types.P;
  managers: types.User[];
  authenticatedUser?: types.User;
  countries: types.Countries;
};

const UserForm = ({
  onSubmit,
  onErrors,
  submit,
  formErrors,
  user,
  managers,
  authenticatedUser,
  countries,
}: UserFormProps): React.ReactElement => {
  let formSubmit: () => Promise<void>;
  let formReset: (nextState?: Partial<FormikState<{ body: string }>>) => void;

  React.useEffect(() => {
    if (submit) {
      formSubmit().then(() => {
        if (formErrors) {
          onErrors(formErrors);
        }
      });
    }
  }, [submit]);

  const userData = filterNulls(user);

  return (
    <Formik
      initialValues={userData}
      validationSchema={UserSchema}
      enableReinitialize={true}
      validateOnChange={false}
      validateOnBlur={false}
      onSubmit={(values, { setSubmitting }) => {
        onSubmit({
          values: values,
          onSuccess: () => {
            Object.keys(values).forEach((key) => (values[key] = ""));
            formReset(values);
          },
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
        submitForm,
        resetForm,
      }) => {
        formSubmit = submitForm;
        formReset = resetForm;

        return (
          <div className="user__form">
            <form onSubmit={handleSubmit}>
              <div className="field">
                <label className="label">Manager</label>
                <div className="control is-expanded">
                  <div className="select">
                    <select
                      name="manager_id"
                      onChange={handleChange}
                      onBlur={handleBlur}
                      value={values.manager_id}
                    >
                      <option>Select manager</option>
                      {managers.map((manager) => (
                        <option
                          key={`manager-${manager.id}`}
                          value={manager.id}
                        >
                          {manager.name}
                        </option>
                      ))}
                    </select>
                    {errors.manager_id && (
                      <p className="help is-danger">{errors.manager_id}</p>
                    )}
                    {formErrors.manager_id && (
                      <p className="help is-danger">{formErrors.manager_id}</p>
                    )}
                  </div>
                </div>
              </div>
              <div className="field">
                <label className="label">Country</label>
                <div className="control is-expanded">
                  <div className="select">
                    <select
                      name="country"
                      onChange={handleChange}
                      onBlur={handleBlur}
                      value={values.country}
                    >
                      <option>Select country</option>
                      {countries.map((entry) => (
                        <option key={`country-${entry[0]}`} value={entry[0]}>
                          {entry[1]}
                        </option>
                      ))}
                    </select>
                    {errors.country && (
                      <p className="help is-danger">{errors.country}</p>
                    )}
                    {formErrors.country && (
                      <p className="help is-danger">{formErrors.country}</p>
                    )}
                  </div>
                </div>
              </div>
              <div className="field">
                <label className="label">Email</label>
                <p className="control is-expanded has-icons-left has-icons-right">
                  <input
                    className="input"
                    name="email"
                    type="email"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.email}
                  />
                  <span className="icon is-small is-left">
                    <i className="fas fa-envelope"></i>
                  </span>
                  {errors.email && (
                    <p className="help is-danger">{errors.email}</p>
                  )}
                  {formErrors.email && (
                    <p className="help is-danger">{formErrors.email}</p>
                  )}
                </p>
              </div>
              <div className="field">
                <label className="label">First name</label>
                <p className="control is-expanded has-icons-left">
                  <input
                    className="input"
                    name="first_name"
                    type="text"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.first_name}
                  />
                  <span className="icon is-small is-left">
                    <i className="fas fa-user"></i>
                  </span>
                  {errors.first_name && (
                    <p className="help is-danger">{errors.first_name}</p>
                  )}
                </p>
              </div>
              <div className="field">
                <label className="label">Last name</label>
                <p className="control is-expanded has-icons-left">
                  <input
                    className="input"
                    name="last_name"
                    type="text"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.last_name}
                  />
                  <span className="icon is-small is-left">
                    <i className="fas fa-user"></i>
                  </span>
                  {errors.last_name && (
                    <p className="help is-danger">{errors.last_name}</p>
                  )}
                </p>
              </div>
              <div className="field">
                <label className="label">Phone number</label>
                <p className="control is-expanded has-icons-left">
                  <input
                    className="input"
                    name="phone_number"
                    type="text"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.phone_number}
                    disabled={!!(user && user.phone_number)}
                  />
                  <span className="icon is-small is-left">
                    <i className="fas fa-phone"></i>
                  </span>
                  {errors.phone_number && (
                    <p className="help is-danger">{errors.phone_number}</p>
                  )}
                  {formErrors.phone_number && (
                    <p className="help is-danger">{formErrors.phone_number}</p>
                  )}
                </p>
              </div>
              <div className="field">
                <label className="label">Active campaign ID</label>
                <p className="control is-expanded has-icons-left">
                  <input
                    className="input"
                    name="active_campaign_id"
                    type="text"
                    value={values.active_campaign_id}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <span className="icon is-small is-left">
                    <i className="fas fa-info-circle"></i>
                  </span>
                  {errors.active_campaign_id && (
                    <p className="help is-danger">
                      {errors.active_campaign_id}
                    </p>
                  )}
                  {formErrors.active_campaign_id && (
                    <p className="help is-danger">
                      {formErrors.active_campaign_id}
                    </p>
                  )}
                </p>
              </div>
            </form>
          </div>
        );
      }}
    </Formik>
  );
};

export default withFormikValidator<UserFormProps, types.Error[]>(UserForm);
