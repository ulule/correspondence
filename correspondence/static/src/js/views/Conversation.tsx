import * as React from "react";

import ConversationProfile from "./ConversationProfile";
import ThreadContainer from "./ThreadContainer";
import { useAtomValue } from "jotai";
import { conversationAtom } from "../atoms";

type ConversationProps = {
  messageFormFocus: boolean;
};

export default function Conversation({
  messageFormFocus,
}: ConversationProps): React.ReactElement {
  const conversation = useAtomValue(conversationAtom);

  return (
    <div className="conversation__container">
      <div className="conversation__wrapper">
        <ThreadContainer
          messageFormFocus={messageFormFocus}
        />
      </div>
      {conversation && conversation.receiver && (
        <ConversationProfile
          user={conversation.receiver}
        />
      )}
    </div>
  );
}
