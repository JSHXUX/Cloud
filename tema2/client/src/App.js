import React, { useState } from "react";
const SERVER_IP = "http://localhost:8080";


//Bakugan API
function Bakugan() {
  const [bakuganData, setBakuganData] = useState("");

  const [getRoute, setGetRoute] = useState("");

  const [postName, setPostName] = useState("");
  const [postGPower, setPostGPower] = useState("");
  const [postAttribute, setPostAttribute] = useState("");

  const [postRareName, setPostRareName] = useState("");

  const [put1Name, setPut1Name] = useState("");
  const [put1GPower, setPut1GPower] = useState("");

  const [put2Name, setPut2Name] = useState("");
  const [put2Attribute, setPut2Attribute] = useState("");

  const [deleteRoute, setDeleteRoute] = useState("");


  const getAllBakugan = async () => {
    try {
      const response = await fetch(`${SERVER_IP}/bakugan/`);
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    }
  };

  const getBakugan = async () => {
    if (!getRoute.trim()) {
      setBakuganData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/bakugan/${getRoute}`);
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    } finally {
      setGetRoute("");
    }
  };

  const postBakugan = async () => {
    if (!postName.trim() || !postGPower.trim() || !postAttribute.trim()) {
      setBakuganData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/bakugan/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: postName,
          gPower: postGPower,
          attribute: postAttribute,
        }),
      });
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    } finally {
      setPostName("");
      setPostGPower("");
      setPostAttribute("");
    }
  };

  const postRareBakugan = async () => {
    if (!postRareName.trim()) {
      setBakuganData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/bakugan/rare/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: postRareName,
        }),
      });
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    } finally {
      setPostRareName("");
    }
  };

  const putBakuganGPower = async () => {
    if (!put1Name.trim() || !put1GPower.trim()) {
      setBakuganData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/bakugan/gPower/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: put1Name,
          gPower: put1GPower,
        }),
      });
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    } finally {
      setPut1Name("");
      setPut1GPower("");
    }
  };

  const putBakuganAttribute = async () => {
    if (!put2Name.trim() || !put2Attribute.trim()) {
      setBakuganData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/bakugan/attribute/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: put2Name,
          attribute: put2Attribute,
        }),
      });
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    } finally {
      setPut2Name("");
      setPut2Attribute("");
    }
  };

  const deleteBakugan = async () => {
    if (!deleteRoute.trim()) {
      setBakuganData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/bakugan/${deleteRoute}`, {
        method: "DELETE",
      });
      const data = await response.json();
      setBakuganData(JSON.stringify(data, null, 2));
    } catch (error) {
      setBakuganData("Error fetching Bakugan data.");
    } finally {
      setDeleteRoute("");
    }
  };

  return (
    <div>
      <h2>Bakugan API</h2>
      <div>
        <button onClick={getAllBakugan}>Get All Bakugans</button>
      </div>
      <div>
        <input
          type="text"
          placeholder="Enter Bakugan Name"
          value={getRoute}
          onChange={(e) => setGetRoute(e.target.value)}
        />
        <button onClick={getBakugan}>Get Bakugan</button>
      </div>
      <div>
        <input
          type="text"
          placeholder="Enter Bakugan Name"
          value={postName}
          onChange={(e) => setPostName(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter Bakugan GPower"
          value={postGPower}
          onChange={(e) => setPostGPower(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter Bakugan Attribute"
          value={postAttribute}
          onChange={(e) => setPostAttribute(e.target.value)}
        />
        <button onClick={postBakugan}>Create Bakugan</button>
      </div>
      <div>
        <input
          type="text"
          placeholder="Enter Rare Bakugan Name"
          value={postRareName}
          onChange={(e) => setPostRareName(e.target.value)}
        />
        <button onClick={postRareBakugan}>Create Rare Bakugan</button>
      </div>
      <div>
        <input
          type="text"
          placeholder="Enter Bakugan Name"
          value={put1Name}
          onChange={(e) => setPut1Name(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter Bakugan GPower"
          value={put1GPower}
          onChange={(e) => setPut1GPower(e.target.value)}
        />
        <button onClick={putBakuganGPower}>Update Bakugan gPower</button>
      </div>
      <div>
        <input
          type="text"
          placeholder="Enter Bakugan Name"
          value={put2Name}
          onChange={(e) => setPut2Name(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter Bakugan Attribute"
          value={put2Attribute}
          onChange={(e) => setPut2Attribute(e.target.value)}
        />
        <button onClick={putBakuganAttribute}>Update Bakugan attribute</button>
      </div>
      <div>
        <input
          type="text"
          placeholder="Enter Bakugan Name"
          value={deleteRoute}
          onChange={(e) => setDeleteRoute(e.target.value)}
        />
        <button onClick={deleteBakugan}>Delete Bakugan</button>
      </div>
      <pre>{bakuganData}</pre>
    </div>
  );
}


// Weather API
function Weather() {
  const [city, setCity] = useState("");
  const [weatherData, setWeatherData] = useState("");

  const getWeather = async () => {
    if (!city.trim()) {
      setWeatherData("Please enter a valid Input.");
      return;
    }

    try {
      const response = await fetch(`${SERVER_IP}/weather?city=${city}`);
      const data = await response.json();
      const temp = data["main"]["temp"];
      const description = data["weather"][0]["description"];
      setWeatherData(JSON.stringify({"temperature": temp, "description": description}, null, 2));
    } catch (error) {
      setWeatherData("Error fetching weather data.");
    } finally {
      setCity("");
    }
  };

  return (
    <div>
      <h2>Weather API</h2>
      <input
        type="text"
        placeholder="Enter city"
        value={city}
        onChange={(e) => setCity(e.target.value)}
      />
      <button onClick={getWeather}>Get Weather Data</button>
      <pre>{weatherData}</pre>
    </div>
  );
}


// Useless API
function UselessFact() {
  const [uselessFact, setUselessFact] = useState("");

  const getUselessFact = async () => {
    try {
      const response = await fetch(`${SERVER_IP}/useless/`);
      const data = await response.json();
      setUselessFact(data.text || "No fact available.");
    } catch (error) {
      setUselessFact("Error fetching useless fact.");
    }
  };

  return (
    <div>
      <h2>Useless Fact API</h2>
      <button onClick={getUselessFact}>Get Useless Fact</button>
      <p>{uselessFact}</p>
    </div>
  );
}


function App() {
  return (
    <div className="App">
      <h1>Some APIs... 👻</h1>
      <Bakugan />
      <Weather />
      <UselessFact />
    </div>
  );
}


export default App;
