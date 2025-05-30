import * as React from "react";
import ConversationItem from "./ConversationItem";
import classNames from "classnames";
import { getConversations } from "../api";
import { Conversation, PageMeta } from "../types";
import { AppContext } from "../contexts";
import { useAtomValue, useAtom } from "jotai";
import { conversationAtom, isNewConversation } from "../atoms";

type ConversationListProps = {};

type State = {
  data: Conversation[];
  managerId: number | null;
  loading: boolean;
  initial: boolean;
  meta: PageMeta;
};

export default function ConversationList({}: ConversationListProps): React.ReactElement {
  const initialState: State = {
    data: [],
    managerId: null,
    loading: true,
    initial: true,
    meta: { count: 0, next: null, total: 0, offset: 0 },
  };
  const [isNew, setIsNewConversation] = useAtom(isNewConversation);

  const [conversations, setConversations] = React.useState<State>(initialState);

  const { authenticatedUser, organization } = React.useContext(AppContext);

  const conversation = useAtomValue(conversationAtom);

  const filters = [
    {
      label: "All conversations",
      onClick: () => {
        loadConversations({});
      },
      isActive: !conversations.managerId,
      key: "all-conversations",
    },
    {
      label: "My conversations",
      onClick: () => {
        loadConversations({ managerId: authenticatedUser.id });
      },
      isActive: conversations.managerId,
      key: "my-conversations",
    },
  ];

  const conversationsEndRef = React.useRef(null);

  const onScroll = async () => {
    if (conversations.meta.next === null) {
      return;
    }

    const offset = conversations.meta.offset + 20;

    const page = await getConversations({
      organizationSlug: organization.slug,
      managerId: conversations.managerId,
      offset: offset,
    });

    setConversations({
      data: [...conversations.data, ...page.data],
      managerId: conversations.managerId,
      meta: page.meta,
      loading: false,
      initial: false,
    });
  };

  const handleScroll = () => {
    const element = conversationsEndRef.current;

    if (element.scrollHeight - element.scrollTop == element.clientHeight) {
      onScroll();
    }
  };

  const loadConversations = async ({ managerId }: { managerId?: number }) => {
    setConversations({
      ...conversations,
      ...{ initial: false, loading: true },
    });

    const page = await getConversations({
      organizationSlug: organization.slug,
      managerId: managerId,
    });

    setConversations({
      data: page.data,
      managerId: managerId,
      meta: page.meta,
      loading: false,
      initial: false,
    });
  };

  React.useEffect(() => {
    if (!conversations.initial) {
      return;
    }

    loadConversations({});
  });

  if (conversation) {
    let conversationList = conversations.data;

    const index = conversations.data.findIndex(
      (conv) => conv.receiver.id == conversation.receiver.id
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
            <a
              className="button is-active is-link"
              onClick={() => {
                setIsNewConversation(true);
              }}
            >
              <span>New</span>
              <span className="icon is-small">
                <i className="fas fa-plus"></i>
              </span>
            </a>
          )}
          {isNew && (
            <a
              className="button is-danger"
              onClick={() => {
                setIsNewConversation(false);
              }}
            >
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
          {filters.map((filter) => {
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
          {conversations.data.map((conv) => {
            const klass = classNames({
              conversation__item: true,
              "conversation__item--active":
                conversation && conversation.id == conv.id,
              "conversation__item--unread": conv.unread,
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
}
