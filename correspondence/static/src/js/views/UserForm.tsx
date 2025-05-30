import * as React from "react";
import * as Yup from "yup";
import { Formik } from "formik";
import * as types from "../types";
import { AppContext } from "../contexts";
import sanitize from "../utils/sanitize";
import { updateUser, createUser } from "../api";
import { useSetAtom } from "jotai";
import { userAtom, userFormSubmmitting } from "../atoms";
import { useNavigate } from "react-router";

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
  submit: boolean;
  onSubmit: () => void;
};

const UserForm = ({
  user,
  submit,
  onSubmit,
}: UserFormProps): React.ReactElement => {
  const userData = filterNulls(user);

  const { managers, countries, organization } = React.useContext(AppContext);

  const [formErrors, setFormErrors] = React.useState<Record<string, any>>();

  const setUserFormSubmitting = useSetAtom(userFormSubmmitting);

  let formSubmit: () => Promise<void>;

  const setUser = useSetAtom(userAtom);

  const navigate = useNavigate();

  React.useEffect(() => {
    if (submit) {
      formSubmit();
    }
  }, [submit]);

  return (
    <Formik
      initialValues={userData}
      validationSchema={UserSchema}
      enableReinitialize={true}
      validateOnChange={false}
      validateOnBlur={false}
      onSubmit={async (rawValues, { setSubmitting }) => {
        onSubmit();
        const values = sanitize(rawValues);

        try {
          setUserFormSubmitting(true);
          let isNew = false;

          if (user) {
            const updatedUser = await updateUser({
              userId: user.id,
              values: {
                first_name: values.first_name,
                last_name: values.last_name,
                active_campaign_id: values.active_campaign_id,
                email: values.email,
                phone_number: values.phone_number,
                manager_id: values.manager_id,
                country: values.country,
              },
            });

            setUser(updatedUser);
          } else {
            user = await createUser({
              organizationSlug: organization.slug,
              values: sanitize(values),
            });

            isNew = true;
          }

          setUserFormSubmitting(false);
          setFormErrors({});

          if (isNew) {
            navigate(
              `/organizations/${organization.slug}/conversations/${user.id}/`
            );
          }
        } catch (e) {
          const rawErrors = e.response.data?.detail as types.Error[];

          const results = rawErrors.reduce((accumulator, field) => {
            return {
              ...accumulator,
              [field.loc[field.loc.length - 1]]: field.msg,
            };
          }, {});

          setUserFormSubmitting(false);
          setFormErrors(results);
        }
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
                    {formErrors && formErrors.manager_id && (
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
                    {formErrors && formErrors.country && (
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
                  {formErrors && formErrors.email && (
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
                  {formErrors && formErrors.phone_number && (
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
                  {formErrors && formErrors.active_campaign_id && (
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

export default UserForm;
