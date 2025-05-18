import React, { useState } from "react";
import Avatar from "../components/Avatar";
import SvgActiveCampaign from "../icons/SvgActiveCampaign";
import UserForm from "./UserForm";
import classNames from "classnames";

const ConversationProfile = ({
  user,
  onSubmit,
  errors,
  managers,
  countries
} = props) => {
  const [submit, setSubmit] = useState(false);

  const onErrors = values => {
    setSubmit(false);
  };

  return (
    <div className="conversation__profile">
      {user && (
        <>
          <div className="conversation__profile__avatar">
            <Avatar name={user.name} size="5rem" borderRadius="100%" />
          </div>
          <div className="conversation__profile__information">
            <strong>{user.name}</strong>
            <span>{user.phone_number}</span>
          </div>

          <div className="conversation__profile__identity">
            <UserForm
              user={user}
              onSubmit={onSubmit}
              submit={submit}
              onErrors={onErrors}
              errors={errors}
              managers={managers}
              countries={countries}
            />

            <div className="field is-grouped conversation__profile__buttons">
              <div className="control">
                <button
                  className={classNames({
                    button: true,
                    "is-success": true,
                    "is-loading": submit
                  })}
                  onClick={() => {
                    setSubmit(true);
                  }}
                >
                  <span className="icon is-small">
                    <i className="fas fa-check"></i>
                  </span>
                  <span>Save</span>
                </button>
              </div>
            </div>
          </div>

          <div className="conversation__profile__links">
            <ul>
              {user.active_campaign_id && (
                <li>
                  <a
                    href={`https://ulule.activehosted.com/app/contacts/${user.active_campaign_id}`}
                    className="has-icon"
                    target="_blank"
                    re="noopener noreferrer"
                  >
                    <SvgActiveCampaign className="icon__activecampaign" />
                    <span>Active campaign contact</span>
                  </a>
                </li>
              )}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default ConversationProfile;
