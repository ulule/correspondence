import * as React from "react";

import ConversationProfile from "./ConversationProfile";
import ThreadContainer from "./ThreadContainer";
import * as types from "../types";

type ConversationProps = {
  conversation: types.Conversation;
  isNew: boolean;
  onUserUpdate: (ev: types.OnUserUpdateEvent) => void;
  errors: types.Error[];
  managers: types.User[];
  selectedUsers: types.User[];
  messageFormFocus: boolean;
  countries: types.Countries;
};

export default function Conversation({
  conversation,
  isNew,
  onUserUpdate,
  errors,
  managers,
  selectedUsers,
  messageFormFocus,
  countries,
}: ConversationProps): React.ReactElement {
  return (
    <div className="conversation__container">
      <div className="conversation__wrapper">
        <ThreadContainer
          conversation={conversation}
          messageFormFocus={messageFormFocus}
          selectedUsers={selectedUsers}
        />
      </div>
      {!isNew && (
        <ConversationProfile
          errors={errors}
          managers={managers}
          countries={countries}
          user={conversation && conversation.receiver}
          onSubmit={onUserUpdate}
        />
      )}
    </div>
  );
}
