import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { UserContext } from './UserContext';

function PostDetailPage() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState("");
  const [newComment, setNewComment] = useState("");
  const { username } = useContext(UserContext);

  const fetchPost = () => {
    fetch(`http://localhost:8000/posts/${id}`, { credentials: 'include' })
      .then(res => {
        if (!res.ok) {
          throw new Error("Failed to fetch post details");
        }
        return res.json();
      })
      .then(data => setPost(data))
      .catch(err => setError(err.message));
  };

  useEffect(() => {
    fetchPost();
  }, [id]);

  const handleCommentSubmit = (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    fetch(`http://localhost:8000/posts/${id}/comments`, {
      method: "POST",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: newComment })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(data => { throw new Error(data.detail || 'Error creating comment'); });
      }
      return res.json();
    })
    .then(() => {
      setNewComment("");
      fetchPost(); // Re-fetch to update comments
    })
    .catch(err => setError(err.message));
  };

  const handleVote = (commentId, isUpvote) => {
    fetch(`http://localhost:8000/comments/${commentId}/vote`, {
      method: "POST",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_upvote: isUpvote })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(data => { throw new Error(data.detail || 'Error voting'); });
      }
      return res.json();
    })
    .then(() => {
      fetchPost(); // re-fetch post to update scores
    })
    .catch(err => setError(err.message));
  };

  if (error) {
    return <div className="container mt-5 text-center"><p>{error}</p></div>;
  }

  if (!post) {
    return <div className="container mt-5 text-center"><p>Loading...</p></div>;
  }

  return (
    <div className="container mt-5">
      <h1>{post.title}</h1>
      <p><strong>Creator:</strong> {post.creator}</p>
      {post.image_url && (
        <img 
          src={`http://localhost:8000${post.image_url}`} 
          alt={post.title} 
          style={{maxWidth: "100%", border: "1px solid #ddd", padding: "10px", marginBottom: "20px"}}
        />
      )}
      <p><strong>Description:</strong> {post.description || "N/A"}</p>
      <p><strong>Material:</strong> {post.material || "N/A"}</p>
      <p><strong>Length: (cm)</strong> {post.length || "N/A"} cm</p>
      <p><strong>Width: (cm)</strong> {post.width || "N/A"} cm</p>
      <p><strong>Height: (cm)</strong> {post.height || "N/A"} cm</p>
      <p><strong>Weight: (kg)</strong> {post.weight || "N/A"} kg</p>
      <p><strong>Color:</strong> {post.color || "N/A"}</p>
      <p><strong>Shape:</strong> {post.shape || "N/A"}</p>
      <p><strong>Location:</strong> {post.location || "N/A"}</p>
      <p><strong>Smell:</strong> {post.smell || "N/A"}</p>
      <p><strong>Taste:</strong> {post.taste || "N/A"}</p>
      <p><strong>Origin:</strong> {post.origin || "N/A"}</p>
      <div>
        <h3>Tags:</h3>
        {post.tags.length > 0 ? (
            <ul>
            {post.tags && post.tags.map((tag, index) => (
            <li key={index} className="mb-2">
                {tag.wikidata_url ? (
                <a
                    href={tag.wikidata_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#007bff", textDecoration: "underline", fontWeight: "bold" }}
                >
                    {tag.label}
                </a>
                ) : (
                <span style={{ fontWeight: "bold", color: "#6c757d" }}>{tag.label}</span>
                )}
                {tag.description && (
                <p style={{ marginTop: "5px", fontSize: "0.9rem", color: "#6c757d" }}>
                    {tag.description}
                </p>
                )}
            </li>
            ))}
            </ul>
        ) : (
            <p>No tags available.</p>
        )}
        </div>

        <hr />
        <h2>Comments</h2>
        {post.comments.length === 0 && <p>No comments yet.</p>}
        {post.comments.map(comment => {
        let scoreClass, scoreText;
        if (comment.score > 0) {
            scoreClass = "text-success";
            scoreText = `+${comment.score}`;
        } else if (comment.score < 0) {
            scoreClass = "text-danger";
            scoreText = `${comment.score}`;
        } else {
            scoreClass = "text-secondary";
            scoreText = "0";
        }

        return (
            <div key={comment.id} className="mb-3 border p-2">
            <p><strong>{comment.user.username}:</strong> {comment.content}</p>
            <p>Score: <span className={scoreClass}>{scoreText}</span></p>
            <div className="d-flex gap-2">
                <button 
                type="button" 
                className="btn btn-sm btn-outline-success" 
                onClick={() => handleVote(comment.id, true)}
                >
                Upvote
                </button>
                <button 
                type="button" 
                className="btn btn-sm btn-outline-danger" 
                onClick={() => handleVote(comment.id, false)}
                >
                Downvote
                </button>
            </div>
            </div>
        );
        })}

      {username ? (
        <form onSubmit={handleCommentSubmit} className="mt-4">
          <div className="mb-3">
            <label htmlFor="newComment" className="form-label">Add a Comment</label>
            <textarea 
              id="newComment" 
              className="form-control" 
              value={newComment} 
              onChange={e => setNewComment(e.target.value)} 
              rows="3"
              placeholder="Write your comment here..."
            ></textarea>
          </div>
          <button type="submit" className="btn btn-primary">Submit Comment</button>
        </form>
      ) : (
        <p className="mt-4">Please <a href="/login">login</a> to comment.</p>
      )}
    </div>
  );
}

export default PostDetailPage;
