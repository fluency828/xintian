import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


# create zip file from list of figs
def figs2zip(figs) -> bytes:
    """THIS WILL BE RUN ON EVERY SCRIPT RUN"""
    import io 
    import zipfile
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(file=zip_buf, mode='w', compression=zipfile.ZIP_DEFLATED) as z:
        for i,fig in enumerate(figs):
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            filename = f'{i}.png'
            z.writestr(zinfo_or_arcname=filename, data=buf.getvalue() )
            buf.close()
    
    buf = zip_buf.getvalue()
    zip_buf.close()
    return buf