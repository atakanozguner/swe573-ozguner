import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import debounce from "lodash.debounce"; // Import lodash debounce
import Select from "react-select";


function CreatePostPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [material, setMaterial] = useState("");
  const [length, setLength] = useState("");
  const [width, setWidth] = useState("");
  const [height, setHeight] = useState("");
  const [color, setColor] = useState("");
  const [shape, setShape] = useState("");
  const [weight, setWeight] = useState("");
  const [location, setLocation] = useState("");
  const [smell, setSmell] = useState("");
  const [taste, setTaste] = useState("");
  const [origin, setOrigin] = useState("");
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");
  const [tags, setTags] = useState([]);
  const [options, setOptions] = useState([]);

  const searchTags = debounce((inputValue) => {
    if (inputValue) {
      fetch(`${process.env.REACT_APP_BACKEND_URL}/tags/search?query=${inputValue}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      })
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch tags");
          return res.json();
        })
        .then((data) => {
          console.log(data);
          const newOptions = data.map((tag) => ({
            value: tag.label,
            label: `${tag.label} - ${tag.description || "No description"}`,
          }));
          setOptions(newOptions);
        })
        .catch((err) => console.error("Error fetching tags:", err));
    } else {
      setOptions([]); // Reset options if input is cleared
    }
  }, 500); // 500ms delay to debounce API requests


  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("title", title);
    if (description) formData.append("description", description);
    if (material) formData.append("material", material);
    if (length) formData.append("length", length);
    if (width) formData.append("width", width);
    if (height) formData.append("height", height);
    if (color) formData.append("color", color);
    if (shape) formData.append("shape", shape);
    if (weight) formData.append("weight", weight);
    if (location) formData.append("location", location);
    if (smell) formData.append("smell", smell);
    if (taste) formData.append("taste", taste);
    if (origin) formData.append("origin", origin);
    if (image) formData.append("image", image);
    if (tags) tags.forEach((tag) => formData.append("tags", tag.value));


    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/posts`, {
      method: "POST",
      credentials: 'include',
      body: formData
    });

    if (response.ok) {
      setMessage("Post created successfully!");
      // Redirect to posts page after a short delay
      setTimeout(() => {
        navigate("/posts");
      }, 1000);
    } else {
      const data = await response.json();
      setMessage(`Error: ${data.detail || 'Unable to create post'}`);
    }
  };

  return (
    <div className="container mt-5" style={{ paddingBottom: "100px" }}>
      <h1>Create a New Post</h1>
      {message && <div className="alert alert-info mt-3">{message}</div>}
      <form onSubmit={handleSubmit} className="mt-4" encType="multipart/form-data">
        <div className="mb-3">
          <label className="form-label">Title (required)</label>
          <input type="text" className="form-control" value={title} onChange={e => setTitle(e.target.value)} required />
        </div>

        <div className="mb-3">
          <label className="form-label">Description</label>
          <textarea className="form-control" value={description} onChange={e => setDescription(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Material</label>
          <input type="text" className="form-control" value={material} onChange={e => setMaterial(e.target.value)} />
        </div>

        <div className="mb-3">
            <label className="form-label">Length ( cm )</label>
            <input type="text" className="form-control" value={length} onChange={e => setLength(e.target.value)} />
        </div>

        <div className="mb-3">
            <label className="form-label">Width ( cm )</label>
            <input type="text" className="form-control" value={width} onChange={e => setWidth(e.target.value)} />
        </div>

        <div className="mb-3">
            <label className="form-label">Height ( cm )</label>
            <input type="text" className="form-control" value={height} onChange={e => setHeight(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Color</label>
          <input type="text" className="form-control" value={color} onChange={e => setColor(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Shape</label>
          <input type="text" className="form-control" value={shape} onChange={e => setShape(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Weight ( kg )</label>
          <input type="text" className="form-control" value={weight} onChange={e => setWeight(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Location</label>
          <input type="text" className="form-control" value={location} onChange={e => setLocation(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Smell</label>
          <input type="text" className="form-control" value={smell} onChange={e => setSmell(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Taste</label>
          <input type="text" className="form-control" value={taste} onChange={e => setTaste(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Origin</label>
          <input type="text" className="form-control" value={origin} onChange={e => setOrigin(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Image</label>
          <input type="file" className="form-control" onChange={e => setImage(e.target.files[0])} />
        </div>

        <Select
            isMulti
            options={options}
            onInputChange={(inputValue, { action }) => {
                if (action === "input-change") searchTags(inputValue);
            }}
            onChange={setTags}
            placeholder="Search and add tags"
            noOptionsMessage={() => "No tags found"}
            getOptionLabel={(e) => e.label}
            getOptionValue={(e) => e.value}
        />


        <button type="submit" className="btn btn-success w-100">Create Post</button>
      </form>
    </div>
  );
}

export default CreatePostPage;
