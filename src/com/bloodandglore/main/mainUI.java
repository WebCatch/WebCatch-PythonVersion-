package com.bloodandglore.main;
import java.util.Date; 
import java.util.Calendar; 
import java.awt.event.*;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;


import com.bloodandglore.model.*;

import java.awt.*;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.*;

public class mainUI extends JFrame  implements ActionListener{
	
	
	
	private JTextField jtfURL, jtfJDBC, jtfDBUser, jtfDBPass; //���� , ����,����
	//private JLabel jlbst,jlbblk[][],jlbtime;//��ǰ��Ϸ״̬ , ���Ӱ�ť(��ʾ�Ѿ��㿪),��ǰ������
	private JButton jbtExtract,jbtConnect; //ok��ť ���ڿ�ʼ��Ϸ
	private static mainUI frame;  //������
	private JTable jtData = new JTable();
	private JPanel jpWeb = new JPanel(), jpDB = new JPanel(); //p2��Ϸ���, p1���ƺ�״̬���
	public mainUI(){		
		jpWeb.setLayout(new BorderLayout()); //���ƺ�״̬��岼��
		JPanel jpWebCtrl=new JPanel(); //�������
		jpWebCtrl.add(new JLabel("URL:"));
		jpWebCtrl.add(jtfURL = new JTextField(20));
		jpWebCtrl.add(jbtExtract = new JButton("Extract"));
		jpWeb.add(jpWebCtrl,BorderLayout.NORTH);
		JPanel jpWebData=new JPanel(); //״̬���		
		jpWebData.add(jtData); //��û����ռ� ����״̬
		jpWeb.add(jpWebData,BorderLayout.SOUTH);
		getContentPane().add(jpWeb);
		jbtExtract.addActionListener(this);
	}
	public static void main(String[] args){
		frame=new mainUI();
		frame.setSize(1000,600);
		frame.pack();
		frame.setVisible(true);
		frame.setResizable(false);  //���ɴ���ı��С
		frame.setTitle("WebExtract v1.0");		
		
	}  
	public void actionPerformed(ActionEvent e){		   
		if(e.getSource()==jbtExtract){	 
			ExtractModel extracter = new ExtractModel();			
			String codeBuf = extracter.getHtmlContent(jtfURL.getText().trim(),"utf-8");	 //�õ�Դ����
			String [][] tmptable = extracter.extractTable(codeBuf);  //��������Դ��������ȡ����
			if (tmptable.length > 0){
				jtData = new JTable(tmptable.length,tmptable[0].length);
			}
			updateUITable(jtData, tmptable);
		}
	}
}
