import ure as re
import picoweb

app = picoweb.WebApp(__name__)

@app.route("/")
def index(req, resp):
    headers = {"X-MyHeader1": "foo", "X-MyHeader2":"bar"}

    yield from picoweb.start.response(resp, headers=headers)
    yield from resp.awrite(b"""\
    <!DOCTYPE html>
<html>
<head>
<title>RainbowWarriorSettings</title>
<link rel="stylesheet" href="bootstrap.min.css" >
<link href="style.css" rel="stylesheet">
</head>
<body class="h-100">
<div class="ground"></div>
<div class="sky">
  <div class="cloud variant-1"></div>
  <div class="cloud variant-2"></div>
  <div class="cloud variant-3"></div>
  <div class="cloud variant-4"></div>
  <div class="cloud variant-5"></div>
</div>
<div class="rainbow-preloader">
  <div class="rainbow-stripe"></div>
  <div class="rainbow-stripe"></div>
  <div class="rainbow-stripe"></div>
  <div class="rainbow-stripe"></div>
  <div class="rainbow-stripe"></div>
  <div class="shadow"></div>
  <div class="shadow"></div>
</div>

<div class="text-white align-items-center container d-flex flex-column h-100 justify-content-end pb-md-5">
  <h1 class="">RainbowWarrior</h1>
  <div class="mt-3">

    <form method="POST" action="/" >
      <h3 class="mb-3">Select Color Pattern:</h3>

      <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" type="radio" id="light1" name="light" value="RainbowCycle">RainbowCycle</label>
      </div>

      <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" type="radio" id="light2" name="light" value="Fire">Fire</label>
      </div>

      <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" type="radio" id="light3" name="light" value="MeteorRain">MeteorRain</label>
      </div>

      <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" type="radio" id="light4" name="light" value="ColorGradient">ColorGradient</label>
      </div>

      <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" type="radio" id="light5" name="light" value="Off">Turn LEDs off</label>
      </div>

      <div class="my-4">
        <input class="btn btn-primary" type="submit" name="li" value="Submit color"></b>
      </div>
    </form>
  </div>
</div>
</body>
</html>
""")

@app.route(re.compile('^\/(.+\.css)$'))
def styles(req, resp):
    file_path = req.url_match.group(1)
    headers = b"Cache-Control: max-age=86400   "
    if b"gzip" in req.headers.get(b"Accept-Encoding",b""):
        file_path += ".gz"
        headers += b"Content-Encoding: gzip   "
    print("sending " + file_path)
    yield from app.sendfile(resp, "www/" + file_path, "text/css", headers)

import logging
logging.basicConfig(level=logging.DEBUG)

app.run(debug=True)
