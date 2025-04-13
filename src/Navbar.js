// src/Navbar.js
import React, { useContext } from "react";
import { UserContext } from "./UserContext";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const { user } = useContext(UserContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await auth.signOut();
    navigate("/login");
  };

  return (
    <nav>
      <ul>
        <li>
          {user ? (
            <div>
              <p>Signed in as: {user.email}</p>
              <button onClick={handleLogout}>Logout</button>
            </div>
          ) : (
            <button onClick={() => navigate("/login")}>Login</button>
          )}
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
