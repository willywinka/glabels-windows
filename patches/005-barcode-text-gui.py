#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "src").resolve()

def read(rel):
    p = ROOT / rel
    if not p.exists():
        raise RuntimeError(f"missing source file: {p}")
    return p, p.read_text(encoding="utf-8")

def write(p, text):
    p.write_text(text, encoding="utf-8")

def insert_after(text, needle, addition, label):
    if addition.strip() in text:
        print(f"[skip] {label} already present")
        return text
    pos = text.find(needle)
    if pos < 0:
        raise RuntimeError(f"{label}: anchor not found: {needle!r}")
    pos += len(needle)
    print(f"[ok] {label}")
    return text[:pos] + addition + text[pos:]

def function_slice(text, signature, next_signature=None):
    start = text.find(signature)
    if start < 0:
        raise RuntimeError(f"function not found: {signature}")
    if next_signature:
        end = text.find(next_signature, start + len(signature))
        if end < 0:
            raise RuntimeError(f"next function not found after {signature}: {next_signature}")
    else:
        end = len(text)
    return start, end

def insert_after_in_function(text, signature, needle, addition, label, next_signature=None):
    if addition.strip() in text:
        print(f"[skip] {label} already present")
        return text
    start, end = function_slice(text, signature, next_signature)
    sub = text[start:end]
    pos = sub.find(needle)
    if pos < 0:
        raise RuntimeError(f"{label}: anchor not found inside {signature}: {needle!r}")
    pos = start + pos + len(needle)
    print(f"[ok] {label}")
    return text[:pos] + addition + text[pos:]

p, text = read("glabels/ObjectEditor.cpp")

include_block = """
#include <QCheckBox>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QFontComboBox>
#include <QHBoxLayout>"""
if "#include <QFontComboBox>" not in text:
    text = insert_after(text, "#include <QFileDialog>", include_block, "ObjectEditor includes")

constructor_code = r"""
                //
                // Human-readable barcode text controls.
                //
                auto* barcodeFontFamilyCombo = new QFontComboBox( barcodePage );
                barcodeFontFamilyCombo->setObjectName( "barcodeFontFamilyCombo" );
                formLayout_6->addRow( tr("Font:"), barcodeFontFamilyCombo );

                auto* barcodeFontSizeSpin = new QDoubleSpinBox( barcodePage );
                barcodeFontSizeSpin->setObjectName( "barcodeFontSizeSpin" );
                barcodeFontSizeSpin->setDecimals( 1 );
                barcodeFontSizeSpin->setRange( 1.0, 200.0 );
                barcodeFontSizeSpin->setSingleStep( 0.5 );
                barcodeFontSizeSpin->setSuffix( " pt" );
                barcodeFontSizeSpin->setValue( 10.0 );
                formLayout_6->addRow( tr("Size:"), barcodeFontSizeSpin );

                auto* barcodeFontStyleWidget = new QWidget( barcodePage );
                auto* barcodeFontStyleLayout = new QHBoxLayout( barcodeFontStyleWidget );
                barcodeFontStyleLayout->setContentsMargins( 0, 0, 0, 0 );

                auto* barcodeFontBoldCheck = new QCheckBox( tr("Bold"), barcodeFontStyleWidget );
                barcodeFontBoldCheck->setObjectName( "barcodeFontBoldCheck" );
                auto* barcodeFontItalicCheck = new QCheckBox( tr("Italic"), barcodeFontStyleWidget );
                barcodeFontItalicCheck->setObjectName( "barcodeFontItalicCheck" );
                auto* barcodeFontUnderlineCheck = new QCheckBox( tr("Underline"), barcodeFontStyleWidget );
                barcodeFontUnderlineCheck->setObjectName( "barcodeFontUnderlineCheck" );

                barcodeFontStyleLayout->addWidget( barcodeFontBoldCheck );
                barcodeFontStyleLayout->addWidget( barcodeFontItalicCheck );
                barcodeFontStyleLayout->addWidget( barcodeFontUnderlineCheck );
                formLayout_6->addRow( tr("Style:"), barcodeFontStyleWidget );

                auto* barcodeTextAlignCombo = new QComboBox( barcodePage );
                barcodeTextAlignCombo->setObjectName( "barcodeTextAlignCombo" );
                barcodeTextAlignCombo->addItem( tr("Left"), int(Qt::AlignLeft) );
                barcodeTextAlignCombo->addItem( tr("Center"), int(Qt::AlignHCenter) );
                barcodeTextAlignCombo->addItem( tr("Right"), int(Qt::AlignRight) );
                barcodeTextAlignCombo->setCurrentIndex( 1 );
                formLayout_6->addRow( tr("Alignment:"), barcodeTextAlignCombo );

                connect( barcodeFontFamilyCombo, SIGNAL(currentFontChanged(QFont)),
                         this, SLOT(onBarcodeControlsChanged()) );
                connect( barcodeFontSizeSpin, SIGNAL(valueChanged(double)),
                         this, SLOT(onBarcodeControlsChanged()) );
                connect( barcodeFontBoldCheck, SIGNAL(toggled(bool)),
                         this, SLOT(onBarcodeControlsChanged()) );
                connect( barcodeFontItalicCheck, SIGNAL(toggled(bool)),
                         this, SLOT(onBarcodeControlsChanged()) );
                connect( barcodeFontUnderlineCheck, SIGNAL(toggled(bool)),
                         this, SLOT(onBarcodeControlsChanged()) );
                connect( barcodeTextAlignCombo, SIGNAL(currentIndexChanged(int)),
                         this, SLOT(onBarcodeControlsChanged()) );
"""
text = insert_after_in_function(
    text,
    "ObjectEditor::ObjectEditor( QWidget *parent )",
    "                setupUi( this );",
    constructor_code,
    "create barcode font controls",
    "        void ObjectEditor::setModel(",
)

load_code = r"""
                        auto* barcodeFontFamilyCombo =
                                barcodePage->findChild<QFontComboBox*>("barcodeFontFamilyCombo");
                        auto* barcodeFontSizeSpin =
                                barcodePage->findChild<QDoubleSpinBox*>("barcodeFontSizeSpin");
                        auto* barcodeFontBoldCheck =
                                barcodePage->findChild<QCheckBox*>("barcodeFontBoldCheck");
                        auto* barcodeFontItalicCheck =
                                barcodePage->findChild<QCheckBox*>("barcodeFontItalicCheck");
                        auto* barcodeFontUnderlineCheck =
                                barcodePage->findChild<QCheckBox*>("barcodeFontUnderlineCheck");
                        auto* barcodeTextAlignCombo =
                                barcodePage->findChild<QComboBox*>("barcodeTextAlignCombo");

                        barcodeFontFamilyCombo->setCurrentFont( QFont( mObject->fontFamily() ) );
                        barcodeFontSizeSpin->setValue( mObject->fontSize() );
                        barcodeFontBoldCheck->setChecked( mObject->fontWeight() == QFont::Bold );
                        barcodeFontItalicCheck->setChecked( mObject->fontItalicFlag() );
                        barcodeFontUnderlineCheck->setChecked( mObject->fontUnderlineFlag() );

                        const int barcodeAlignIndex =
                                barcodeTextAlignCombo->findData( int(mObject->textHAlign()) );
                        barcodeTextAlignCombo->setCurrentIndex(
                                barcodeAlignIndex >= 0 ? barcodeAlignIndex : 1 );
"""
text = insert_after_in_function(
    text,
    "        void ObjectEditor::loadBarcodePage()",
    "                        barcodeChecksumCheck->setChecked( csFlag );",
    load_code,
    "load barcode font controls",
    "        void ObjectEditor::loadShadowPage()",
)

change_code = r"""
                        auto* barcodeFontFamilyCombo =
                                barcodePage->findChild<QFontComboBox*>("barcodeFontFamilyCombo");
                        auto* barcodeFontSizeSpin =
                                barcodePage->findChild<QDoubleSpinBox*>("barcodeFontSizeSpin");
                        auto* barcodeFontBoldCheck =
                                barcodePage->findChild<QCheckBox*>("barcodeFontBoldCheck");
                        auto* barcodeFontItalicCheck =
                                barcodePage->findChild<QCheckBox*>("barcodeFontItalicCheck");
                        auto* barcodeFontUnderlineCheck =
                                barcodePage->findChild<QCheckBox*>("barcodeFontUnderlineCheck");
                        auto* barcodeTextAlignCombo =
                                barcodePage->findChild<QComboBox*>("barcodeTextAlignCombo");

                        mObject->setFontFamily( barcodeFontFamilyCombo->currentFont().family() );
                        mObject->setFontSize( barcodeFontSizeSpin->value() );
                        mObject->setFontWeight(
                                barcodeFontBoldCheck->isChecked() ? QFont::Bold : QFont::Normal );
                        mObject->setFontItalicFlag( barcodeFontItalicCheck->isChecked() );
                        mObject->setFontUnderlineFlag( barcodeFontUnderlineCheck->isChecked() );
                        mObject->setTextHAlign(
                                Qt::Alignment( barcodeTextAlignCombo->currentData().toInt() ) );
"""
text = insert_after_in_function(
    text,
    "        void ObjectEditor::onBarcodeControlsChanged()",
    "                        mObject->setBcChecksumFlag( csFlag );",
    change_code,
    "save barcode font controls to model",
    "        void ObjectEditor::onBarcodeInsertFieldKeySelected(",
)

write(p, text)

p, text = read("model/ModelBarcodeObject.cpp")

if "#include <QFontMetricsF>" not in text:
    text = insert_after(text, "#include <QDebug>", "\n#include <QFontMetricsF>", "QFontMetricsF include")
if "#include <algorithm>" not in text:
    text = insert_after(text, '#include "glbarcode/QtRenderer.hpp"', "\n#include <algorithm>", "algorithm include")

copy_code = r"""
                mTextFontFamily        = object->mTextFontFamily;
                mTextFontSize          = object->mTextFontSize;
                mTextFontWeight        = object->mTextFontWeight;
                mTextFontItalicFlag    = object->mTextFontItalicFlag;
                mTextFontUnderlineFlag = object->mTextFontUnderlineFlag;
                mTextHAlign            = object->mTextHAlign;
"""
text = insert_after_in_function(
    text,
    "ModelBarcodeObject::ModelBarcodeObject( const ModelBarcodeObject* object )",
    "                mBcColorNode    = object->mBcColorNode;",
    copy_code,
    "copy barcode font properties",
    "        ///\n        /// Clone",
)
write(p, text)

p, text = read("model/XmlLabelCreator.cpp")
creator_code = r"""
                XmlUtil::setStringAttr( node, "font_family", object->fontFamily() );
                XmlUtil::setDoubleAttr( node, "font_size", object->fontSize() );
                XmlUtil::setWeightAttr( node, "font_weight", object->fontWeight() );
                XmlUtil::setBoolAttr( node, "font_italic", object->fontItalicFlag() );
                XmlUtil::setBoolAttr( node, "font_underline", object->fontUnderlineFlag() );
                XmlUtil::setAlignmentAttr( node, "align", object->textHAlign() );
"""
text = insert_after_in_function(
    text,
    "void XmlLabelCreator::createObjectBarcodeNode(",
    '                XmlUtil::setBoolAttr( node, "checksum", object->bcChecksumFlag() );',
    creator_code,
    "serialize barcode font properties",
    "        void XmlLabelCreator::createObjectTextNode(",
)
write(p, text)

p, text = read("model/XmlLabelParser.cpp")
parser_attrs = r"""
                QString       fontFamily        = XmlUtil::getStringAttr( node, "font_family", "Sans" );
                double        fontSize          = XmlUtil::getDoubleAttr( node, "font_size", 10.0 );
                QFont::Weight fontWeight        =
                        XmlUtil::getWeightAttr( node, "font_weight", QFont::Normal );
                bool          fontItalicFlag    =
                        XmlUtil::getBoolAttr( node, "font_italic", false );
                bool          fontUnderlineFlag =
                        XmlUtil::getBoolAttr( node, "font_underline", false );
                Qt::Alignment textHAlign =
                        XmlUtil::getAlignmentAttr( node, "align", Qt::AlignHCenter );
"""
text = insert_after_in_function(
    text,
    "XmlLabelParser::parseObjectBarcodeNode( const QDomElement &node )",
    '                bool bcChecksumFlag = XmlUtil::getBoolAttr( node, "checksum", true );',
    parser_attrs,
    "parse barcode font properties",
    "        ModelTextObject*",
)

start, end = function_slice(
    text,
    "XmlLabelParser::parseObjectBarcodeNode( const QDomElement &node )",
    "        ModelTextObject*",
)
sub = text[start:end]

if "object->setFontFamily( fontFamily );" not in sub:
    lines = sub.splitlines(keepends=True)

    return_i = None
    for i, line in enumerate(lines):
        if "return new ModelBarcodeObject(" in line:
            return_i = i
            break

    if return_i is None:
        raise RuntimeError("replace barcode parser return: start line not found")

    return_j = None
    for j in range(return_i, min(return_i + 12, len(lines))):
        if ");" in lines[j]:
            return_j = j
            break

    if return_j is None:
        raise RuntimeError("replace barcode parser return: end line not found")

    indent = lines[return_i][:len(lines[return_i]) - len(lines[return_i].lstrip())]

    replacement = [
        f"{indent}auto* object = new ModelBarcodeObject( x0, y0, w, h, lockAspectRatio,\n",
        f"{indent}                                             bcStyle, bcTextFlag, bcChecksumFlag, bcData, bcColorNode,\n",
        f"{indent}                                             QTransform( a[0], a[1], a[2], a[3], a[4], a[5] ) );\n",
        f"{indent}object->setFontFamily( fontFamily );\n",
        f"{indent}object->setFontSize( fontSize );\n",
        f"{indent}object->setFontWeight( fontWeight );\n",
        f"{indent}object->setFontItalicFlag( fontItalicFlag );\n",
        f"{indent}object->setFontUnderlineFlag( fontUnderlineFlag );\n",
        f"{indent}object->setTextHAlign( textHAlign );\n",
        f"{indent}return object;\n",
    ]

    lines[return_i:return_j + 1] = replacement
    sub = "".join(lines)
    text = text[:start] + sub + text[end:]
    print("[ok] restore barcode font properties after XML load")
else:
    print("[skip] XML restore already present")

write(p, text)

print("Barcode text GUI/font patching completed successfully.")
