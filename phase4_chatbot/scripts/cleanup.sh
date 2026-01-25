#!/bin/bash
# Phase IV - Cleanup Script
# Removes all deployment resources

set -e

echo "============================================="
echo "  Phase IV - Cleanup"
echo "============================================="

# Uninstall Helm release
echo ""
echo "[1/3] Uninstalling Helm release..."
if helm list | grep -q "todo-chatbot"; then
    helm uninstall todo-chatbot
    echo "Helm release uninstalled."
else
    echo "No Helm release found."
fi

# Delete secrets
echo ""
echo "[2/3] Deleting secrets..."
if kubectl get secret todo-chatbot-secrets >/dev/null 2>&1; then
    kubectl delete secret todo-chatbot-secrets
    echo "Secrets deleted."
else
    echo "No secrets found."
fi

# Optional: Stop Minikube
echo ""
echo "[3/3] Minikube cleanup..."
read -p "Do you want to stop Minikube? (y/N): " STOP_MINIKUBE
if [ "$STOP_MINIKUBE" = "y" ] || [ "$STOP_MINIKUBE" = "Y" ]; then
    minikube stop
    echo "Minikube stopped."

    read -p "Do you want to delete Minikube cluster? (y/N): " DELETE_MINIKUBE
    if [ "$DELETE_MINIKUBE" = "y" ] || [ "$DELETE_MINIKUBE" = "Y" ]; then
        minikube delete
        echo "Minikube cluster deleted."
    fi
fi

echo ""
echo "============================================="
echo "  Cleanup Complete!"
echo "============================================="
