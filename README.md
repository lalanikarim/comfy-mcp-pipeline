# Comfy MCP Pipeline

This is a [pipeline](https://docs.openwebui.com/pipelines/) wrapper for [comfy-mcp-server](https://pypi.org/project/comfy-mcp-server/) for [Open WebUI](https://docs.openwebui.com/).

## Prerequisites

- [Open WebUI](https://docs.openwebui.com/getting-started/quick-start)
- [Open WebUI Pipelines](https://docs.openwebui.com/pipelines/#-quick-start-with-docker)
- [ComfyUI](https://www.comfy.org/download)
- Updated [requirements.txt] for pipelines server
- JSON Export of a ComfyUI Workflow API - see sample for reference [workflow.json]
    - From Comfy UI, select a workflow to export
    - From the top menu, `Workflow` -> `Export (API)` -> provide a filename -> `Confirm`
    - This file will need to be uploaded to the pipeline server

## Pipeline Installation and Setup

- Follow Open WebUI Pipelines documentation to upload the [comfy-mcp-pipeline.py] to Pipeline server
- Choose `comfy-mcp-pipeline (pipe)` from `Pipeline Valves`
- Set configuration for the following valves:
    - Comfy Url: Url for your Comfy UI server
    - Comfy Workflow Json File: path of the workflow JSON file
    - Prompt Node Id: Id of the text prompt node from workflow JSON file
    - Output Node Id: Id of the generated image node from the workflow JSON file
- If all steps are successfull, you will see `Comfy MCP Pipeline` in the list of models

## Usage

- Select `New Chat` and select `Comfy MCP Pipeline`
- Enter an image generation prompt and hit send
- If the setup was successful you should see the generated image 


