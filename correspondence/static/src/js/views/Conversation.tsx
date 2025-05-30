import * as React from "react";

import ConversationProfile from "./ConversationProfile";
import ThreadContainer from "./ThreadContainer";
import * as types from "../types";
import { useAtomValue } from "jotai";
import { conversationAtom } from "../atoms";

type ConversationProps = {
  onUserUpdate: (ev: types.OnUserUpdateEvent) => void;
  errors: types.Error[];
  selectedUsers: types.User[];
  messageFormFocus: boolean;
};

export default function Conversation({
  onUserUpdate,
  errors,
  selectedUsers,
  messageFormFocus,
}: ConversationProps): React.ReactElement {
  const conversation = useAtomValue(conversationAtom);

  const isNew = conversation && conversation.id === 0

  return (
    <div className="conversation__container">
      <div className="conversation__wrapper">
        <ThreadContainer
          messageFormFocus={messageFormFocus}
          selectedUsers={selectedUsers}
        />
      </div>
      {!isNew && (
        <ConversationProfile
          user={conversation.receiver}
          errors={errors}
          onSubmit={onUserUpdate}
        />
      )}
    </div>
  );
}
