import React, { useState } from 'react';

function DiseasePredictor() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [imagePreview, setImagePreview] = useState(null); // State to store the image preview

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    
    // Generate image preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result); // Set the image preview URL
    };
    if (selectedFile) {
      reader.readAsDataURL(selectedFile); // Read file as data URL for preview
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('http://localhost:5000/predict_disease', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div className="predictor">
      <h2>Upload Image for Disease Prediction</h2>
      
      {/* Image Preview */}
      {imagePreview && (
        <div className="image-preview">
          <img src={imagePreview} alt="Uploaded Preview" width="300" />
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} required />
        <button type="submit">Predict</button>
      </form>
      
      {result && (
        <div className="result">
          <h3>Disease: {result.disease_name}</h3>
          <p>Confidence: {result.confidence}%</p>
          <p>Fertilizer: {result.fertilizer}</p>

          <p className="alert_one">{result.alert_one}</p>
          
          <ul>
            {result.description && result.description.map((measure, index) => (
              <li key={index}>{measure}</li>
            ))}
          </ul>

          <ul>
            {result.description_marathi && result.description_marathi.map((measure, index) => (
              <li key={index} className="description_marathi">{measure}</li>
            ))}
          </ul>

          <p className="alert_two">{result.alert_two}</p>
          
          <ul>
            {result.preventive_measures && result.preventive_measures.map((measure, index) => (
              <li key={index}>{measure}</li>
            ))}
          </ul>

          <ul>
            {result.preventive_measures_marathi && result.preventive_measures_marathi.map((measure, index) => (
              <li key={index} className="preventive_measures_marathi">{measure}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default DiseasePredictor;
