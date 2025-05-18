import React, { useState, useRef, useEffect } from "react";
import classNames from "classnames";
import Avatar from "../components/Avatar";
import api from "../api";

const usersInitialState = {
  data: [],
  loading: false,
  search: "",
  meta: { count: 0, next: null, total: 0 }
};

const UserList = ({ onUserAdd, onUserRemove, selectedUsers } = props) => {
  const [typing, setTyping] = useState({ typing: false, timeout: 0 });
  const [users, setUsers] = useState(usersInitialState);

  const handleUserAdd = user => {
    setUsers(usersInitialState);
    searchInputRef.current.value = "";

    onUserAdd(user);
  };

  const onSearchChange = name => {
    if (name === "") {
      setUsers({
        data: [],
        loading: false,
        search: "",
        meta: { count: 0, next: null, total: 0 }
      });

      return;
    }

    setUsers({ ...users, ...{ loading: true, search: name } });

    (async () => {
      const res = await api.get(`/users/?q=${encodeURIComponent(name)}`);
      const data = { ...res.data, ...{ search: name } };

      setUsers(data);
    })();
  };

  const searchInputRef = useRef(null);

  useEffect(() => {
    searchInputRef.current.focus();
  });

  const handleChange = e => {
    clearTimeout(typing.timeout);

    setTyping({
      typing: false,
      timeout: setTimeout(() => {
        onSearchChange(searchInputRef.current.value);
      }, 500)
    });
  };

  return (
    <>
      <div>
        <div className="field">
          <div
            className={classNames({
              control: true,
              userlist__container: true,
              "is-loading": users.loading
            })}
          >
            <span className="icon is-small">
              <i className="fas fa-search"></i>
            </span>
            <div className="userlist">
              <div className="field is-grouped is-grouped-multiline">
                {selectedUsers.map(user => (
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
                    defaultValue={users.search}
                    onChange={handleChange}
                    ref={searchInputRef}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {users.data.length > 0 && (
        <div className="dropdown is-active">
          <div className="dropdown-menu" id="dropdown-menu" role="menu">
            <div className="dropdown-content">
              {users.data.map(user => (
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
};

export default UserList;
