import React, { useState } from 'react';
import './App.css';
import DiseasePredictor from './components/DiseasePredictor';
import FruitDetailsPredictor from './components/FruitDetailsPredictor';

function App() {
  const [currentModel, setCurrentModel] = useState('disease');

  return (
    <div className="App">
      <h1>Plant Disease and Fruit Details Prediction</h1>
      <div className="button-container">
        <button onClick={() => setCurrentModel('disease')}>Disease Prediction</button>
        <button onClick={() => setCurrentModel('fruit')}>Fruit Prediction</button>
      </div>
      <p>                                        </p>
      {currentModel === 'disease' ? <DiseasePredictor /> : <FruitDetailsPredictor />}
    </div>
  );
}

export default App;
