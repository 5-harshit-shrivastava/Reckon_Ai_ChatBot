#!/usr/bin/env python3
"""
Quick test to verify HuggingFace transformers installation
"""

def test_imports():
    """Test that all required packages are available"""
    print("🔍 Testing imports...")

    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False

    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
        return False

    try:
        import sentence_transformers
        print(f"✅ Sentence-Transformers: {sentence_transformers.__version__}")
    except ImportError as e:
        print(f"❌ Sentence-Transformers: {e}")
        return False

    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False

    return True

def test_device():
    """Check available compute devices"""
    print("\n🖥️ Testing compute devices...")

    try:
        import torch

        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("ℹ️ CUDA not available, will use CPU")

        # Test CPU
        device = torch.device("cpu")
        test_tensor = torch.randn(10, 10, device=device)
        print(f"✅ CPU compute working: tensor shape {test_tensor.shape}")

        return True
    except Exception as e:
        print(f"❌ Device test failed: {e}")
        return False

if __name__ == "__main__":
    print("⚡ Quick HuggingFace Setup Test")
    print("=" * 40)

    success = True

    if not test_imports():
        success = False

    if not test_device():
        success = False

    print("\n" + "=" * 40)
    if success:
        print("🎉 All basic tests passed!")
        print("✅ Ready for HuggingFace models")
    else:
        print("❌ Setup issues detected")
        print("💡 Run: pip install transformers torch sentence-transformers numpy")