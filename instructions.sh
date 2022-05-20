#!/bin/env bash

wait_keypress () {
    while :
    do
    read -n 1 a
    printf "\n"
    case $a in
    q* ) exit ;;
    * ) break ;;
    esac
    done
}

clear
echo "Change to the Translation pane, select Algorithm 1 (Metis) and click 'Generate PGT'."
echo "(just click 'OK' in the pop-up)"
echo ""
echo ">> Once done, press any key to continue (or 'q' to quit) in this terminal:"
wait_keypress

echo "In the Translator tab add a deployment target by pressing 'o'"
echo "Click 'Add'"
echo "Put 'Local' into the Deployment Name column"
echo "Put 'http://172.17.0.2:8001' into 'Destination URL' and select 'Direct' as the method."
echo "The red cross should turn into a green tick."
echo "Click 'Save Changes'"
echo "Click on the 'Deploy:Local' button in the upper right corner."
echo ""
echo ">> Once done, press any key to continue (or 'q' to quit) in this terminal:"
wait_keypress

echo "Monitor the deployed graph execution in the DIM window."
echo "In addition you can monitor the node manager log file in another terminal by typing:"
echo "tail -f ~/dlg/logs/dlgNM.log"
echo ""
echo ">> Once the graph is finished press any key (or 'q' to quit) in this terminal to shutdown the containers:"
wait_keypress
