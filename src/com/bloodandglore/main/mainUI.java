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
	
	
	
	private JTextField jtfURL, jtfJDBC, jtfDBUser, jtfDBPass; //行数 , 列数,雷数
	//private JLabel jlbst,jlbblk[][],jlbtime;//当前游戏状态 , 格子按钮(表示已经点开),当前秒表度数
	private JButton jbtExtract,jbtConnect; //ok按钮 用于开始游戏
	private static mainUI frame;  //主窗口
	private JTable jtData = new JTable();
	private JPanel jpWeb = new JPanel(), jpDB = new JPanel(); //p2游戏面板, p1控制和状态面板
	public mainUI(){		
		jpWeb.setLayout(new BorderLayout()); //控制和状态面板布局
		JPanel jpWebCtrl=new JPanel(); //控制面板
		jpWebCtrl.add(new JLabel("URL:"));
		jpWebCtrl.add(jtfURL = new JTextField(20));
		jpWebCtrl.add(jbtExtract = new JButton("Extract"));
		jpWeb.add(jpWebCtrl,BorderLayout.NORTH);
		JPanel jpWebData=new JPanel(); //状态面板		
		jpWebData.add(jtData); //还没申请空间 待定状态
		jpWeb.add(jpWebData,BorderLayout.SOUTH);
		getContentPane().add(jpWeb);
		jbtExtract.addActionListener(this);
	}
	public static void main(String[] args){
		frame=new mainUI();
		frame.setSize(1000,600);
		frame.pack();
		frame.setVisible(true);
		frame.setResizable(false);  //不可窗体改变大小
		frame.setTitle("WebExtract v1.0");		
		
	}  
	public void actionPerformed(ActionEvent e){		   
		if(e.getSource()==jbtExtract){	 
			ExtractModel extracter = new ExtractModel();			
			String codeBuf = extracter.getHtmlContent(jtfURL.getText().trim(),"utf-8");	 //得到源代码
			String [][] tmptable = extracter.extractTable(codeBuf);  //分析并从源代码中提取出表
			if (tmptable.length > 0){
				jtData = new JTable(tmptable.length,tmptable[0].length);
			}
			updateUITable(jtData, tmptable);
		}
	}
}
