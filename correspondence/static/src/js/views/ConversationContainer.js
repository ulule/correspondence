import React from "react";
import Conversation from "./Conversation";
import UserList from "./UserList";
import classNames from "classnames";

const ConversationContainer = ({
  conversation,
  onFocus,
  users,
  isNew,
  onSearchAdd,
  onSearchRemove,
  onAction,
  errors,
  managers,
  onUserUpdate,
  selectedUsers,
  countries
} = props) => {
  const showConversation = conversation || selectedUsers.length > 0;

  return (
    <div className="conversation">
      <div
        className={classNames({ toolbox: true, "toolbox--fullwidth": isNew })}
      >
        <div className="toolbox__item">
          {!isNew && (
            <strong>
              {conversation &&
                conversation.receiver &&
                conversation.receiver.name}
            </strong>
          )}
          {isNew && (
            <UserList
              users={users}
              onUserAdd={onSearchAdd}
              onUserRemove={onSearchRemove}
              selectedUsers={selectedUsers}
            />
          )}
        </div>
        {!isNew && conversation && conversation.id && conversation.unread && (
          <div className="toolbox__item">
            <a
              className="button"
              title="Mark as read"
              onClick={() => {
                onAction("read");
              }}
            >
              <span>Mark as read</span>
            </a>
          </div>
        )}
        {!isNew && conversation && conversation.id && !conversation.unread && (
          <div className="toolbox__item">
            <a
              className="button"
              title="Mark as unread"
              onClick={() => {
                onAction("unread");
              }}
            >
              <span>Mark as unread</span>
            </a>
          </div>
        )}
      </div>

      {showConversation && (
        <Conversation
          conversation={conversation}
          onFocus={onFocus}
          onUserUpdate={onUserUpdate}
          errors={errors}
          managers={managers}
          countries={countries}
          selectedUsers={selectedUsers}
          messageFormFocus={!isNew}
        />
      )}
    </div>
  );
};

export default ConversationContainer;
