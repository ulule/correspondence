import React from "react";

import ConversationProfile from "./ConversationProfile";
import ThreadContainer from "./ThreadContainer";

const Conversation = ({
  conversation,
  isNew,
  onUserUpdate,
  errors,
  managers,
  selectedUsers,
  messageFormFocus,
  countries
} = props) => {
  return (
    <div className="conversation__container">
      <div className="conversation__wrapper">
        <ThreadContainer
          conversation={conversation}
          focus={messageFormFocus}
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
          conversation={conversation}
        />
      )}
    </div>
  );
};

export default Conversation;
