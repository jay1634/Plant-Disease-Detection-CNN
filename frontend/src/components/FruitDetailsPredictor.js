import React, { useState } from 'react';

function FruitDetailsPredictor() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('http://localhost:5000/predict_fruit_details', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div className="predictor">
      <h2>Upload Image for Fruit Details Prediction</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} required />
        <button type="submit">Predict</button>
      </form>
      
      {result && (
        <div className="result">
          <h3>Species: {result.species_name}</h3>
          <p>Ripeness: {result.ripeness}</p>
          <p>Grading: {result.grading}</p>
        </div>
      )}
    </div>
  );
}

export default FruitDetailsPredictor;
