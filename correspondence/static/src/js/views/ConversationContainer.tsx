import * as React from "react";
import Conversation from "./Conversation";
import UserList from "./UserList";
import classNames from "classnames";
import * as types from "../types";
import { useAtomValue } from "jotai";
import { conversationAtom } from "../atoms";

type ConversationContainerProps = {
  onSearchAdd: (user: types.User) => void;
  onSearchRemove: (user: types.User) => void;
  onAction: (action: string) => void;
  selectedUsers: types.User[];
};

export default function ConversationContainer({
  onSearchAdd,
  onSearchRemove,
  onAction,
  selectedUsers,
}: ConversationContainerProps): React.ReactElement {
  const conversation = useAtomValue(conversationAtom);

  const showConversation = conversation || selectedUsers.length > 0;

  const isNew = conversation && conversation.id === 0;

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
          selectedUsers={selectedUsers}
          messageFormFocus={!isNew}
        />
      )}
    </div>
  );
}
