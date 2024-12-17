import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function PostsPage() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/posts", {
      credentials: 'include'
    })
    .then(res => {
      if (!res.ok) {
        throw new Error("Failed to fetch posts");
      }
      return res.json();
    })
    .then(data => setPosts(data))
    .catch(err => setError(err.message));
  }, []);

  if (error) {
    return <div className="container mt-5 text-center"><p>Error: {error}</p></div>;
  }

  return (
    <div className="container mt-5">
      <h1>Posts</h1>
      <div className="mb-3 text-end">
        <Link to="/posts/new" className="btn btn-success">Create New Post</Link>
      </div>
      {posts.length === 0 && <p>No posts available yet.</p>}
      <div className="row">
        {posts.map(post => (
          <div className="col-md-4 mb-4" key={post.id}>
            <div className="card">
              {post.image_url && (
                // Use full URL if needed: `http://localhost:8000` + post.image_url
                <img src={`http://localhost:8000${post.image_url}`} className="card-img-top" alt={post.title} />
              )}
              <div className="card-body">
                <h5 className="card-title">{post.title}</h5>
                <Link to={`/posts/${post.id}`} className="btn btn-primary">View Details</Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PostsPage;
