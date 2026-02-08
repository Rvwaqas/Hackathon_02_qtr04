#!/bin/bash
# Phase V Part B - Cleanup Script
# Removes all deployment resources including Dapr

set -e

echo "============================================="
echo "  Phase V Part B - Cleanup"
echo "============================================="

# Uninstall Helm release
echo ""
echo "[1/4] Uninstalling Helm release..."
if helm list | grep -q "todo-chatbot"; then
    helm uninstall todo-chatbot
    echo "Helm release uninstalled."
else
    echo "No Helm release found."
fi

# Delete secrets
echo ""
echo "[2/4] Deleting secrets..."
if kubectl get secret todo-chatbot-secrets >/dev/null 2>&1; then
    kubectl delete secret todo-chatbot-secrets
    echo "Secrets deleted."
else
    echo "No secrets found."
fi

# Uninstall Dapr
echo ""
echo "[3/4] Dapr cleanup..."
read -p "Do you want to uninstall Dapr from cluster? (y/N): " UNINSTALL_DAPR
if [ "$UNINSTALL_DAPR" = "y" ] || [ "$UNINSTALL_DAPR" = "Y" ]; then
    dapr uninstall -k 2>/dev/null || true
    echo "Dapr uninstalled."
fi

# Optional: Stop Minikube
echo ""
echo "[4/4] Minikube cleanup..."
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
