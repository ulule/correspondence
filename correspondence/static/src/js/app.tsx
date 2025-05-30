import "@fortawesome/fontawesome-free/js/all";
import * as ReactDOM from "react-dom/client";
import * as React from "react";

import { getManagers } from "./api";

import ConversationWrapper from "./views/ConversationWrapper";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Countries, Organization, User } from "./types";
import { AppContext } from "./contexts";
import UserCreate from "./views/UserCreate";

function Conversations(): React.ReactElement {
  return (
    <div className="conversations">
      <div className="conversations__wrapper">
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

window.addEventListener("DOMContentLoaded", () => {
  (async () => {
    const managers = await getManagers();

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
        <UserCreate />
        <Conversations />
      </AppContext>
    );
  })();
});
