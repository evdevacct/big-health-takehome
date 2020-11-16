### Setup
* Create virtual environment
* Activate virtual environment
* `pip install -r requirements.txt`
* Create the supplied `.env.json` file

### Sample Use
`python main.py 10`

`pytest` to run tests.

File streams are written as temps.txt and averages.txt in the top level folder.

The process is heavily I/O bound with the Weather API as the pipeline runs sequentially for each tweet. The most obvious optimization would be to bring in the asyncio event loop and update the SlidingAverageCalculator to manage tweets coming in out-of-order. More tests should be added different tweet shapes, as well as the pipeline function.

A simple way to deploy could be by placing the application in a Docker container and creating a scheduled task on FarGate, which has schedule system and avoids the need to manage machines.