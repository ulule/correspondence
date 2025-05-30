import * as React from "react";
import { parseISO, formatDistanceToNow } from "date-fns";
import Avatar from "../components/Avatar";
import { Link, useParams } from "react-router-dom";
import { Conversation } from "../types";
import { AppContext } from "../contexts";

type ConversationItemProps = {
  conversation: Conversation;
};

export default function ConversationItem({
  conversation,
}: ConversationItemProps): React.ReactElement {
  const { receiver, last_message } = conversation;

  let createdAt;

  if (!last_message) {
    createdAt = parseISO(conversation.created_at);
  } else {
    createdAt = parseISO(last_message.created_at);
  }

  const { organization } = React.useContext(AppContext);

  return (
    <Link
      to={`/organizations/${organization.slug}/conversations/${conversation.receiver.id}`}
    >
      <div className="conversation__item-container">
        <header className="conversation__item__head">
          <div className="conversation__item__user__avatar">
            <Avatar name={receiver.name} />
          </div>
          <div className="conversation__item__user">
            <div className="conversation__item__user__information">
              <strong>{receiver.name}</strong>
              <span>{receiver.phone_number}</span>
            </div>
          </div>
          <div className="conversation__item__last-message-at">
            {formatDistanceToNow(createdAt, { addSuffix: true })}
          </div>
        </header>
        <div className="conversation__item__body">
          {last_message && last_message.body}
        </div>
        <div className="conversation__item__stats">
          {conversation.messages_count} message
          {conversation.messages_count === 1 ? "" : "s"}
        </div>
      </div>
    </Link>
  );
}
