#!/bin/bash
# Script för att skapa n8n-automations projektet på din hemdator

echo "🚀 Skapar n8n-automations projektet..."

# Ta bort eventuellt gammalt repo från hemkatalogen
cd ~
if [ -d ".git" ]; then
    echo "⚠️  Tar bort gammalt git-repo från hemkatalogen..."
    rm -rf .git README.md
fi

# Skapa projekt-mapp
mkdir -p ~/n8n-automations
cd ~/n8n-automations

# Initiera git
git init
git branch -M main

echo "✅ Mappen skapad. Nu behöver du hämta filerna..."
echo ""
echo "📋 Kör följande kommandon:"
echo ""
echo "1. Ladda ner projektet från servern:"
echo "   scp -r user@taborsen.duckdns.org:/home/albin/n8n-automations/* ~/n8n-automations/"
echo ""
echo "2. Eller klona från GitHub igen när det är klart:"
echo "   cd ~ && rm -rf n8n-automations"
echo "   git clone https://github.com/albjo840/n8n-automations.git"
echo ""
