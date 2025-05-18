import React, { useRef, useEffect, useState } from "react";
import ConversationItem from "./ConversationItem";
import classNames from "classnames";
import ConversationModel from "../models/ConversationModel";
import api from "../api";

const ConversationList = ({
  conversation,
  onNewClick,
  isNew,
  authenticatedUser,
  organization
} = props) => {
  const [conversations, setConversations] = useState({
    data: [],
    managerId: null,
    loading: true,
    initial: true,
    meta: { count: 0, next: null, total: 0, offset: 0 }
  });

  const filters = [
    {
      label: "All conversations",
      onClick: () => {
        loadConversations();
      },
      isActive: !conversations.managerId,
      key: "all-conversations"
    },
    {
      label: "My conversations",
      onClick: () => {
        loadConversations({ managerId: authenticatedUser.id });
      },
      isActive: conversations.managerId,
      key: "my-conversations"
    }
  ];

  const conversationsEndRef = useRef(null);

  const onScroll = async () => {
    if (conversations.meta.next === null) {
      return;
    }

    const offset = parseInt(conversations.meta.offset || 0, 10) + 20;

    let url = `/organizations/${organization.slug}/conversations/?offset=${offset}&limit=20`;

    const managerId = conversations.managerId;

    if (managerId) {
      url = `${url}&manager_id=${managerId}`;
    }

    const res = await api.get(url);

    const data = res.data;

    setConversations({
      ...data,
      ...{
        data: [...conversations.data, ...data.data].map(conv =>
          ConversationModel(conv)
        ),
        managerId: managerId
      }
    });
  };

  const handleScroll = () => {
    const element = conversationsEndRef.current;

    if (element.scrollHeight - element.scrollTop == element.clientHeight) {
      onScroll();
    }
  };

  const loadConversations = async (props = {}) => {
    setConversations({
      ...conversations,
      ...{ initial: false, loading: true }
    });

    let url = `/organizations/${organization.slug}/conversations/`;

    const { managerId } = props;

    if (managerId) {
      url = `${url}?manager_id=${props.managerId}`;
    }

    const res = await api.get(url);
    const data = res.data;

    setConversations({
      ...data,
      ...{
        data: data.data.map(conv => ConversationModel(conv)),
        managerId: managerId
      }
    });
  };

  useEffect(() => {
    if (!conversations.initial) {
      return;
    }

    loadConversations();
  });

  if (conversation) {
    let conversationList = conversations.data;

    const index = conversations.data.findIndex(
      conv => conv.receiver.id == conversation.receiver.id
    );

    if (index === -1) {
      conversationList = [conversation, ...conversationList];
    } else {
      conversationList.splice(index, 1, conversation);
    }

    conversations.data = conversationList;
  }

  return (
    <aside className="conversation__list">
      <div className="toolbox">
        <div className="toolbox__content">
          <strong>
            {conversations.meta.total} conversation
            {conversations.meta.total === 1 ? "" : "s"}
          </strong>
        </div>
        <p className="buttons">
          {!isNew && (
            <a className="button is-active is-link" onClick={onNewClick}>
              <span>New</span>
              <span className="icon is-small">
                <i className="fas fa-plus"></i>
              </span>
            </a>
          )}
          {isNew && (
            <a className="button is-danger" onClick={onNewClick}>
              <span>Close</span>
              <span className="icon is-small">
                <i className="fas fa-times"></i>
              </span>
            </a>
          )}
        </p>
      </div>
      <div className="tabs is-centered">
        <ul>
          {filters.map(filter => {
            return (
              <li
                key={filter.key}
                className={classNames({ "is-active": filter.isActive })}
              >
                <a onClick={filter.onClick}>{filter.label}</a>
              </li>
            );
          })}
        </ul>
      </div>
      {!conversations.loading && (
        <ul
          className="conversation__list-container"
          onScroll={handleScroll}
          ref={conversationsEndRef}
        >
          {conversations.data.map(conv => {
            const klass = classNames({
              conversation__item: true,
              "conversation__item--active":
                conversation && conversation.id == conv.id,
              "conversation__item--unread": conv.unread
            });

            return (
              <li key={conv.id} className={klass}>
                <ConversationItem conversation={conv} />
              </li>
            );
          })}
        </ul>
      )}
      {conversations.loading && (
        <div className="conversation__list-loader">
          <a className="button is-large is-loading">Loading</a>
        </div>
      )}
    </aside>
  );
};

export default ConversationList;
