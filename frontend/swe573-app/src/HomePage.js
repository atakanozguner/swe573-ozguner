import React, { useContext } from 'react';
import { UserContext } from './UserContext';
import { Link } from 'react-router-dom';

function HomePage() {
  const { username } = useContext(UserContext);
  

  return (
    <div className="container mt-5 text-center">
      {username ? (
        <>
        <h1>Welcome, {username}!</h1>
        <p>Browse existing posts <Link to="/posts">Posts</Link></p>
        </>
      ) : (
        <div>
          <h1>Welcome to SWE573 App</h1>
          <p>Please <Link to="/login">Login</Link> or <Link to="/register">Register</Link> to continue.</p>
        </div>
      )}
    </div>
  );
}

export default HomePage;
