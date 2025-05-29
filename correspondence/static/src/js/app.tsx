import "@fortawesome/fontawesome-free/js/all";
import * as ReactDOM from "react-dom/client";
import * as React from "react";

import { useState } from "react";
import { client, createUser } from "./api";
import Navbar from "./views/Navbar";
import Modal from "./components/Modal";
import UserForm from "./views/UserForm";
import ConversationWrapper from "./views/ConversationWrapper";
import sanitize from "./utils/sanitize";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import {
  Conversation,
  Countries,
  Error,
  OnUserCreateEvent,
  Organization,
  User,
} from "./types";
import { AppContext } from "./contexts";

type State = {
  conversation: Conversation;
  isNewConversation: boolean;
  isNewUser: boolean;
  userCreateErrors: Error[];
};

function Conversations(): React.ReactElement {
  const initialState: State = {
    conversation: null,
    isNewConversation: false,
    isNewUser: false,
    userCreateErrors: [],
  };

  const { organization } = React.useContext(AppContext);

  const [state, setState] = useState<State>(initialState);

  const { isNewUser, userCreateErrors } = state;

  const onUserCreate = async (props: OnUserCreateEvent) => {
    try {
      await createUser({organizationSlug: organization.slug, values: sanitize(props.values)})

      setState({
        ...state,
        ...{ isNewUser: false },
      });

      if (props.onSuccess) {
        props.onSuccess();
      }
    } catch (e) {
      setState({
        ...state,
        ...{ userCreateErrors: e.response.data.detail },
      });
    }
  };

  return (
    <div className="conversations">
      <Navbar
        onUserCreateBtnClick={() => {
          setState({
            ...state,
            ...{ isNewUser: true, userCreateErrors: [] },
          });
        }}
      />
      <Modal
        onCloseClick={() => {
          setState({
            ...state,
            ...{ isNewUser: false },
          });
        }}
        visible={isNewUser}
        title="Create a new contact"
        onSave={onUserCreate}
      >
        <UserForm errors={userCreateErrors} />
      </Modal>

      <BrowserRouter>
        <Routes>
          <Route
            path="/organizations/:slug/conversations?"
            element={<ConversationWrapper />}
          />
          <Route
            path="/organizations/:slug/conversations/:id"
            element={<ConversationWrapper />}
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

declare global {
  interface Window {
    CDE: {
      api: {
        url: string;
      };
      authenticatedUser: User;
      organization: Organization;
      countries: Countries;
    };
  }
}

async function loadManagers(): Promise<User[]> {
  const res = await client.get(`/users/?is_staff=1`);
  return res.data.data;
}

window.addEventListener("DOMContentLoaded", () => {
  (async () => {
    const managers = await loadManagers();

    const { organization, countries } = window.CDE;

    const supportedCountries = countries.filter(
      (entry) => organization.supported_countries.indexOf(entry[0]) !== -1
    );

    const root = ReactDOM.createRoot(
      document.getElementById("conversations-container")
    );

    root.render(
      <AppContext
        value={{
          authenticatedUser: window.CDE.authenticatedUser,
          organization: organization,
          countries: supportedCountries,
          managers: managers,
        }}
      >
        <Conversations />
      </AppContext>
    );
  })();
});
