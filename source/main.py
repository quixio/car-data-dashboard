from datetime import datetime
import pandas as pd

from quixstreaming import *

# Create a client factory. Factory helps you create StreamingClient (see below) a little bit easier
security = SecurityOptions('../certificates/ca.cert', "quixdev-textprocessingbench", "0XfH3dwvcIoYHLIpI2o4gm28jfPWJlCmiBy")
client = StreamingClient('kafka-k1.quix.ai:9093,kafka-k2.quix.ai:9093,kafka-k3.quix.ai:9093', security)

# Open output topic connection.
output_topic = client.open_output_topic('quixdev-textprocessingbench-lorem')

# Create a new stream. A stream is a collection of data that belong to a single session of a single source.
# For example single car journey.
# If you don't specify stream id, random guid is generated.
# Specify it if you want append data into the stream later.
# stream = output_topic.create_stream("my-own-stream-id")
stream = output_topic.create_stream()

# Give the stream human readable name. This name will appear in data catalogue.
stream.properties.name = "cardata"

# Save stream in specific folder in data catalogue to help organize your workspace.
stream.properties.location = "/static data"

# Add stream metadata to add context to time series data.
stream.properties.metadata["circuit"] = "Sakhir Short"
stream.properties.metadata["player"] = "Swal"
stream.properties.metadata["game"] = "Codemasters F1 2019"

df = pd.read_csv("cardata.csv")

# Add TAG__ prefix to column LapNumber to use this column as tag (index).
df = df.rename(columns={"LapNumber" : "TAG__LapNumber" })

# Write data frame to output topic.
stream.parameters.write(df)

print("Closing stream")

# Stream can be infinitely long or have start and end.
# If you send data into closed stream, it is automatically opened again.
stream.close()
