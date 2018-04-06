#!bin/bash
# Workaround for the chrome security issues that some of us were having.
# Launch a mini http server using this script, then use the urls in this
#	directory to open the clients.
echo "Running mini http server on http://localhost:8000/"
echo "It is connected to this directory."
echo "Any of the contents can be accessed through the connection:"
echo ""
ls -1 *.html
echo ""
echo "CTRL+C to quit."
python -m http.server
