import * as React from "react";
import Avatar from "../components/Avatar";
import SvgActiveCampaign from "../icons/SvgActiveCampaign";
import UserForm from "./UserForm";
import classNames from "classnames";
import { User } from "../types";
import { useAtomValue } from "jotai";
import { userAtom, userFormSubmmitting } from "../atoms";

type ConversationProfileProps = {
  user: User;
};

export default function ConversationProfile({
  user,
}: ConversationProfileProps): React.ReactElement {
  const submitting = useAtomValue(userFormSubmmitting);
  const [submit, setSubmit] = React.useState(false);

  user = useAtomValue(userAtom) || user;

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
              submit={submit}
              onSubmit={() => setSubmit(false)}
            />

            <div className="field is-grouped conversation__profile__buttons">
              <div className="control">
                <button
                  className={classNames({
                    button: true,
                    "is-success": true,
                    "is-loading": submitting,
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
                    rel="noopener noreferrer"
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
}
