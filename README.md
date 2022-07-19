# OSD2F Survey Test Station

This is a test environment for the [add-on survey mode](https://github.com/datenfruehstueck/osd2f/) to [OSD2F](https://github.com/uvacw/osd2f). It allows to test and verify the communication processes and workflows described in the [survey.md documentation](https://github.com/datenfruehstueck/osd2f/blob/main/docs/survey.md).

## Installation

Install the requirements and run `main.py`. It will fire up a Quart web interface that will guide you through the remaining steps.  

## Development

Importantly, the web interface asks you (at the very beginning) to enter the URL to the OSD2F installation (in survey mode). A usual development workflow could thus be to have OSD2F running on `127.0.0.1:5000` and this survey station running at `127.0.0.1:5001`. The small yet crucial difference in port numbering (`:5001` and `:5000`) allows for tests across domains which is the strict(er) case than having both installations running on the same server.

## Issues

As this interface only allows for testing, crucial bugs are better reported to [datenfruehstueck/osd2f](https://github.com/datenfruehstueck/osd2f/). Known issues include the currently problematic use of quotation marks in the language specifications.
