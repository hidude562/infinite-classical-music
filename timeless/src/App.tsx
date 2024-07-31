import { useState } from 'react'
import { AutoTokenizer, AutoModel, pipeline } from '@xenova/transformers';
import { env } from '@xenova/transformers';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

env.allowLocalModels=false;

function App() {
  const [count, setCount] = useState(0)
  const [temperature, setTemperature] = useState(0.5)
  const [allMusic, setallMusic] = useState(". renaissance |")

  function handleTemperatureChange(data) {
        setTemperature(data.target.value)
  }

  function generate() {

  }

  async function startGen() {
    let tokenizer = await AutoTokenizer.from_pretrained('hidude562/classical-maestro-onnx-3m');
    let model = await AutoModel.from_pretrained('hidude562/classical-maestro-onnx-3m');
    // [{'label': 'POSITIVE', 'score': 0.999817686}]
  }

  return (
    <>
        <h1>timeless</h1>
        <p>Infinite classical music, generated right in your broswer.</p>
        <input type="range" id="temperature" min="0.01" max="1.0" value="0.7" step="0.01" onChange={handleTemperatureChange}></input>
        <br/>
        <label htmlFor="temperature">Temperature ()</label>
        <br/><br/>
        <button onClick={startGen}>Start</button>
    </>
  )
}

export default App
