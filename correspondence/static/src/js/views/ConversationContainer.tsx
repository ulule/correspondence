import * as React from "react";
import Conversation from "./Conversation";
import UserList from "./UserList";
import classNames from "classnames";
import { useAtom, useAtomValue } from "jotai";
import { markConversation } from "../api";
import {
  conversationAtom,
  isNewConversation,
  selectedUsersAtom,
} from "../atoms";

type ConversationContainerProps = {};

export default function ConversationContainer({}: ConversationContainerProps): React.ReactElement {
  const [conversation, setConversation] = useAtom(conversationAtom);

  const selectedUsers = useAtomValue(selectedUsersAtom);

  const isNew = useAtomValue(isNewConversation);

  const showConversation =
    conversation || (selectedUsers && selectedUsers.length > 0);

  const onAction = async (action: string) => {
    const conv = await markConversation(conversation.id, action);

    setConversation(conv);
  };

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
          {isNew && <UserList />}
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

      {showConversation && <Conversation messageFormFocus={!isNew} />}
    </div>
  );
}
