import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function PostsPage() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");

  const fetchPosts = () => {
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
  };

  const handleInterest = (postId) => {
    fetch(`http://localhost:8000/posts/${postId}/interested`, {
      method: "POST",
      credentials: 'include',
    })
      .then(res => res.json())
      .then(data => {
        // Update the interest count in the post list
        setPosts(prevPosts =>
          prevPosts.map(post =>
            post.id === postId ? { ...post, interest_count: data.interest_count } : post
          )
        );
      })
      .catch(err => console.error("Error toggling interest:", err));
  };

  useEffect(() => {
    fetchPosts();
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
      <div className="mb-3 text-end">
        <Link to="/posts/hot" className="btn btn-success">Hot Posts 🔥</Link>
      </div>
      {posts.length === 0 && <p>No posts available yet.</p>}
      <div className="row">
        {posts.map(post => (
          <div className="col-md-4 mb-4" key={post.id}>
            <div className="card">
              <div style={{ position: "relative" }}>
                {post.image_url && (
                  <img
                    src={`http://localhost:8000${post.image_url}`}
                    className="card-img-top"
                    alt={post.title}
                    style={{ height: "200px", objectFit: "cover" }}
                  />
                )}
                {/* Interested Button */}
                <button
                  onClick={() => handleInterest(post.id)}
                  className="btn btn-light"
                  style={{
                    position: "absolute",
                    bottom: "10px",
                    right: "10px",
                    backgroundColor: "rgba(255, 255, 255, 0.9)",
                    border: "1px solid #ddd",
                    padding: "5px 10px",
                    fontSize: "14px",
                    borderRadius: "5px"
                  }}
                >
                  ❤️ {post.interest_count || 0}
                </button>
              </div>
              <div className="card-body">
                <h5 className="card-title">{post.title}</h5>
                <p className="card-text"><strong>Creator:</strong> {post.creator}</p>
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
