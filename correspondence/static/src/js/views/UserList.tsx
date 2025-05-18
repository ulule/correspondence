import * as React from "react";
import classNames from "classnames";
import Avatar from "../components/Avatar";
import { getConversation, getUsers } from "../api";
import { ListState, User } from "../types";
import { useAtom, useSetAtom } from "jotai";
import { conversationAtom, selectedUsersAtom } from "../atoms";

const usersInitialState: ListState<User> = {
  data: [],
  loading: false,
  params: {
    search: "",
  },
  meta: { count: 0, next: null, total: 0 },
};

type UserListProps = {};

type TypingState = {
  typing: boolean;
  timeout?: NodeJS.Timeout;
};

export default function UserList({}: UserListProps): React.ReactElement {
  const [typing, setTyping] = React.useState<TypingState>({ typing: false });
  const [state, setState] = React.useState<ListState<User>>(usersInitialState);
  const [selectedUsers, setSelectedUsers] = useAtom(selectedUsersAtom);
  const setConversation = useSetAtom(conversationAtom);

  const handleUserAdd = (user: User) => {
    setState(usersInitialState);
    searchInputRef.current.value = "";

    onUserAdd(user);
  };

  const onSearchChange = (name: string) => {
    if (name === "") {
      setState({
        data: [],
        loading: false,
        params: {
          search: ""
        },
        meta: { count: 0, next: null, total: 0 },
      });

      return;
    }

    setState({ ...state, ...{ loading: true, search: name } });

    (async () => {
      const page = await getUsers(encodeURIComponent(name));

      setState({
        data: page.data,
        params: {
          search: name,
        },
        loading: false,
        meta: page.meta,
      });
    })();
  };

  const searchInputRef = React.useRef(null);

  React.useEffect(() => {
    searchInputRef.current.focus();
  });

  const handleChange = () => {
    if (typing.timeout) {
      clearTimeout(typing.timeout);
    }

    setTyping({
      typing: false,
      timeout: setTimeout(() => {
        onSearchChange(searchInputRef.current.value);
      }, 500),
    });
  };

  const { loading, data: users, params } = state;

  const onUserAdd = async (user: User) => {
    const index = (selectedUsers ?? []).findIndex((cur) => cur.id === user.id);

    if (index === -1) {
      const newSelectedUsers = [...(selectedUsers ?? []), user];

      if (newSelectedUsers.length === 1) {
        const conversation = await getConversation(newSelectedUsers[0].id);
        setConversation(conversation);
      }

      setSelectedUsers(newSelectedUsers);
    }
  };

  const onUserRemove = (user: User) => {
    const newSelectedUsers = selectedUsers.filter((cur) => cur.id != user.id);
    setSelectedUsers(newSelectedUsers);
  };

  return (
    <>
      <div>
        <div className="field">
          <div
            className={classNames({
              control: true,
              userlist__container: true,
              "is-loading": loading,
            })}
          >
            <span className="icon is-small">
              <i className="fas fa-search"></i>
            </span>
            <div className="userlist">
              <div className="field is-grouped is-grouped-multiline">
                {selectedUsers &&
                  selectedUsers.map((user) => (
                    <div key={user.id} className="control">
                      <span className="tag is-link is-medium">
                        {user.name}
                        <button
                          onClick={() => onUserRemove(user)}
                          className="delete is-small"
                        ></button>
                      </span>
                    </div>
                  ))}
                <div className="control">
                  <input
                    className="input"
                    type="text"
                    placeholder="Enter a name or a number"
                    defaultValue={params.search ?? ""}
                    onChange={handleChange}
                    ref={searchInputRef}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {users && (
        <div className="dropdown is-active">
          <div className="dropdown-menu" id="dropdown-menu" role="menu">
            <div className="dropdown-content">
              {users.map((user) => (
                <a
                  key={user.id}
                  onClick={() => handleUserAdd(user)}
                  className="dropdown-item"
                >
                  <div className="card">
                    <div className="card-content">
                      <div className="media">
                        <div className="media-left">
                          <figure className="image is-48x48">
                            <Avatar name={user.name} />
                          </figure>
                        </div>
                        <div className="media-content">
                          <p className="title is-5">{user.name}</p>
                          <p className="subtitle is-7">{user.email}</p>
                          <p className="subtitle is-7">{user.phone_number}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
