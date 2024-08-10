import { useState } from 'react'
import { AutoTokenizer, AutoModelForCausalLM, pipeline } from '@xenova/transformers';
import { env } from '@xenova/transformers';
import { Soundfont } from "smplr";
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

env.allowLocalModels=false;



type TrackSymbol = "%" | "^" | "&" | "*" | "(" | ")" | ";" | ":" | "'" | '"' | "{" | "}" | "[" | "]" | string;
type VelocitySymbol = "$" | "#" | "@" | "!" | string;

class Note {
    note: number;
    start: number;
    length: number;
    track: number;
    velocity: number;

    constructor(note: number, start: number, length: number = 100, track: TrackSymbol = "%", velocity: VelocitySymbol = "#") {
        this.note = note;
        this.start = start;
        this.length = length;
        this.track = this.parseTrack(track);
        this.velocity = this.aiToVelocity(velocity);
    }

    parseTrack(track: TrackSymbol): number {

        switch (track) {
            case "%": return 0;
            case "^": return 1;
            case "&": return 2;
            case "*": return 3;
            case ";": return 4;
            case ":": return 5;
            case "'": return 6;
            case '"': return 7;
            case '"': return 8;
            case ')': return 9;
            case "}": return 10;
            case "[": return 11;
            case "]": return 12;
            case "{": return 12;
            default: return 0;
        }
    }

    aiToVelocity(inputChar: VelocitySymbol): number {
        let dynamic = 127;
        switch (inputChar) {
            case "$": dynamic = 127; break;
            case "#": dynamic = 80; break;
            case "@": dynamic = 65; break;
            case "!": dynamic = 50; break;
        }
        return dynamic;
    }
}

class Notes {
    notes: Note[];

    constructor(unparsedNotes: string) {
        this.notes = [];
        const fileTokens = unparsedNotes.split('|');
        let timeMarker = 0;

        for (let i = 0; i < fileTokens.length; i++) {
            if (!fileTokens[i].includes('.')) {
                const valuesArr: (number | string)[] = [];
                let valueBuild = "";

                for (let j = 0; j < fileTokens[i].length; j++) {
                    if (Notes.test_if_num(fileTokens[i][j])) {
                        valueBuild += fileTokens[i][j];
                    } else {
                        if (valueBuild !== "") {
                            valuesArr.push(parseInt(valueBuild));
                            valueBuild = "";
                        }
                        valuesArr.push(fileTokens[i][j]);
                    }
                }

                if (valueBuild !== "") {
                    valuesArr.push(parseInt(valueBuild));
                    valueBuild = "";
                }

                try {
                    const oldTime = valuesArr[0] as number;
                    valuesArr[0] = oldTime + timeMarker;
                    this.notes.push(new Note(
                        valuesArr[4] as string,
                        valuesArr[0] as number,
                        valuesArr[2] as number,
                        valuesArr[3] as number,
                        valuesArr[1] as number
                    ));
                    timeMarker += oldTime;
                } catch (e) {
                    // Handle error if necessary
                }
            }
        }
    }

    static test_if_num(num: string): boolean {
        if (num === "-") return true;
        return !isNaN(parseInt(num));
    }
}


function App() {
  const [count, setCount] = useState(0)
  const [temperature, setTemperature] = useState(0.5)
  const [allMusic, setallMusic] = useState(". renaissance |")
  const context = new AudioContext();
  const harpsichord = new Soundfont(context, { instrument: "harpsichord" });
  var musicTimeIndex = 0

  function handleTemperatureChange(data) {
        setTemperature(data.target.value)
  }

  function generate() {

  }

  function pushToMusic(events) {
      for(var i = 0; i < events.notes.length; i++) {
        let event = events.notes[i]
        console.log(event)
        harpsichord.start({ note: event.note, velocity: event.velocity, time: event.start/800.0 + context.currentTime, duration: event.length/800.0});
      }
  }

  async function startGen() {
    let model = await pipeline('text-generation', 'hidude562/classical-maestro-onnx-3m');

    let output = await model('. renaissance |', {
        max_new_tokens: 50,
        temperature: 0.9,
        do_sample: true
    });

    console.log(output[0].generated_text)

    var events = new Notes(output[0].generated_text)
    events.notes.pop()
    pushToMusic(events)
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
