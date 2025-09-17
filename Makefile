# Professional Makefile for TextConverter Pro
# Simplifies the build and distribution process

.PHONY: help clean build app installer dmg all test

# Default target
help:
	@echo "🚀 TextConverter Pro Build System"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  help      - Show this help message"
	@echo "  clean     - Clean build artifacts"
	@echo "  test      - Run test suite"
	@echo "  app       - Build macOS .app bundle"
	@echo "  installer - Create .pkg installer"
	@echo "  dmg       - Create .dmg disk image"
	@echo "  all       - Build app, installer, and dmg"
	@echo ""
	@echo "Quick start:"
	@echo "  make app      # Build the app"
	@echo "  make all      # Build everything"
	@echo ""

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build dist __pycache__ .pytest_cache
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean completed"

# Run tests
test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v --tb=short
	@echo "✅ Tests completed"

# Build the macOS app bundle
app: clean
	@echo "🏗️ Building macOS app bundle..."
	./scripts/build_app.sh
	@echo "✅ App build completed"

# Create installer package
installer: app
	@echo "📦 Creating installer package..."
	./scripts/create_installer.sh
	@echo "✅ Installer creation completed"

# Create DMG disk image
dmg: app
	@echo "💿 Creating DMG disk image..."
	./scripts/create_dmg.sh
	@echo "✅ DMG creation completed"

# Build everything
all: app installer dmg
	@echo ""
	@echo "🎉 All builds completed successfully!"
	@echo ""
	@echo "Distribution files:"
	@ls -lh dist/*.app dist/*.pkg dist/*.dmg 2>/dev/null || echo "Some files may be missing"
	@echo ""
	@echo "Ready for distribution! 🚀"

# Development helpers
dev-install:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest py2app pillow
	@echo "✅ Development setup completed"

# Quick test run
quick-test:
	@echo "⚡ Running quick tests..."
	python -c "import src.core.converter; print('✅ Core imports working')"
	python -c "import src.ui.menubar_app; print('✅ UI imports working')"
	python -c "import src.utils.settings; print('✅ Utils imports working')"
	@echo "✅ Quick tests passed"

# Version info
version:
	@echo "📋 TextConverter Pro v1.0.0"
	@echo "   Author: Simone Mattioli"
	@echo "   Repository: https://github.com/simo-hue/TextConverter-Pro"